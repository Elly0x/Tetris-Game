import pygame
import random
import sys

# Inicialização do Pygame
pygame.init()

# Tela e grade
largura_tela = 300
altura_tela = 600
colunas = 10
linhas = 20
tamanho_bloco = largura_tela // colunas

# Cores
preto = (10, 10, 10)
cinza = (50, 50, 50)
branco = (255, 255, 255)
cores = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]

# Formatos das peças
formas = [
    [[[1, 1, 1, 1]]],  # I
    [[[1, 1, 1], [0, 1, 0]]],  # T
    [[[1, 1], [1, 1]]],  # O
    [[[1, 1, 0], [0, 1, 1]]],  # S
    [[[0, 1, 1], [1, 1, 0]]],  # Z
    [[[1, 0, 0], [1, 1, 1]]],  # L
    [[[0, 0, 1], [1, 1, 1]]]   # J
]

class Peca:
    def __init__(self, x, y, forma):
        self.x = x
        self.y = y
        self.forma = forma
        self.cor = random.choice(cores)
        self.rotacao = 0

    def imagem(self):
        return self.forma[self.rotacao % len(self.forma)]

def criar_grade(trancadas={}):
    grade = [[preto for _ in range(colunas)] for _ in range(linhas)]
    for y in range(linhas):
        for x in range(colunas):
            if (x, y) in trancadas:
                grade[y][x] = trancadas[(x, y)]
    return grade

def converter_formato(peca):
    posicoes = []
    formato = peca.imagem()
    for i, linha in enumerate(formato):
        for j, coluna in enumerate(linha):
            if coluna:
                posicoes.append((peca.x + j, peca.y + i))
    return posicoes

def movimento_valido(peca, grade):
    posicoes_aceitas = [[(j, i) for j in range(colunas) if grade[i][j] == preto] for i in range(linhas)]
    posicoes_aceitas = [j for sub in posicoes_aceitas for j in sub]
    for pos in converter_formato(peca):
        if pos not in posicoes_aceitas and pos[1] >= 0:
            return False
    return True

def limpar_linhas(grade, trancadas):
    linhas_removidas = 0
    for i in range(len(grade)-1, -1, -1):
        linha = grade[i]
        if preto not in linha:
            linhas_removidas += 1
            ind = i
            for j in range(colunas):
                try:
                    del trancadas[(j, i)]
                except:
                    continue
    if linhas_removidas > 0:
        for chave in sorted(trancadas, key=lambda x: x[1])[::-1]:
            x, y = chave
            if y < ind:
                nova_chave = (x, y + linhas_removidas)
                trancadas[nova_chave] = trancadas.pop(chave)
    return linhas_removidas * 100  # 100 pontos por linha

def desenhar_grade(tela, grade):
    for i in range(linhas):
        for j in range(colunas):
            pygame.draw.rect(tela, grade[i][j], (j*tamanho_bloco, i*tamanho_bloco, tamanho_bloco, tamanho_bloco))
    for i in range(linhas):
        pygame.draw.line(tela, cinza, (0, i * tamanho_bloco), (largura_tela, i * tamanho_bloco))
    for j in range(colunas):
        pygame.draw.line(tela, cinza, (j * tamanho_bloco, 0), (j * tamanho_bloco, altura_tela))

def desenhar_pontuacao(tela, pontos):
    fonte = pygame.font.SysFont("comicsans", 30)
    texto = fonte.render(f"Pontos: {pontos}", True, branco)
    tela.blit(texto, (10, 10))

def desenhar_janela(tela, grade, pontos):
    tela.fill(preto)
    desenhar_grade(tela, grade)
    desenhar_pontuacao(tela, pontos)
    pygame.display.update()

def escolher_dificuldade(tela):
    fonte = pygame.font.SysFont("comicsans", 40)
    opcoes = ["1 - Fácil", "2 - Médio", "3 - Difícil"]
    escolhida = None

    while escolhida is None:
        tela.fill(preto)
        for i, opcao in enumerate(opcoes):
            texto = fonte.render(opcao, True, branco)
            tela.blit(texto, (largura_tela/2 - texto.get_width()/2, 150 + i*60))
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    escolhida = 0.7
                elif evento.key == pygame.K_2:
                    escolhida = 0.5
                elif evento.key == pygame.K_3:
                    escolhida = 0.3
    return escolhida

def main():
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    pygame.display.set_caption("Tetris")
    relogio = pygame.time.Clock()

    velocidade = escolher_dificuldade(tela)
    pontos = 0
    trancadas = {}
    grade = criar_grade(trancadas)
    peca_atual = Peca(5, 0, random.choice(formas))
    proxima_peca = Peca(5, 0, random.choice(formas))
    tempo_queda = 0
    rodando = True

    while rodando:
        grade = criar_grade(trancadas)
        tempo_queda += relogio.get_rawtime()
        relogio.tick()

        if tempo_queda / 1000 >= velocidade:
            peca_atual.y += 1
            if not movimento_valido(peca_atual, grade):
                peca_atual.y -= 1
                for pos in converter_formato(peca_atual):
                    trancadas[pos] = peca_atual.cor
                peca_atual = proxima_peca
                proxima_peca = Peca(5, 0, random.choice(formas))
                pontos += limpar_linhas(grade, trancadas)
            tempo_queda = 0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    peca_atual.x -= 1
                    if not movimento_valido(peca_atual, grade):
                        peca_atual.x += 1
                elif evento.key == pygame.K_RIGHT:
                    peca_atual.x += 1
                    if not movimento_valido(peca_atual, grade):
                        peca_atual.x -= 1
                elif evento.key == pygame.K_DOWN:
                    peca_atual.y += 1
                    if not movimento_valido(peca_atual, grade):
                        peca_atual.y -= 1
                elif evento.key == pygame.K_UP:
                    peca_atual.rotacao += 1
                    if not movimento_valido(peca_atual, grade):
                        peca_atual.rotacao -= 1

        for pos in converter_formato(peca_atual):
            if pos[1] >= 0:
                grade[pos[1]][pos[0]] = peca_atual.cor

        desenhar_janela(tela, grade, pontos)

        if any(y < 1 for (x, y) in trancadas):
            rodando = False

    pygame.time.wait(2000)
    pygame.quit()

main()
