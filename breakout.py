import pygame
import math

from enum import Enum

class ColisaoTipo(Enum):
    TRAZ = 1
    BAIXO = 2
    FRENTE = 3
    CIMA = 4

class RaqueteMovimentoTipo(Enum):
    ESQUERDA = 1
    DIREITA = 2
    PARADA = 3

class JogoStatus(Enum):
    GANHOU = 1
    PERDEU = 2
    JOGANDO = 3

class Game:

    PAUSE = "Pausa!"
    GANHOU = "Ganhou! Pressione ESC para jogar novamente..."
    PERDEU = "Perdeu! Pressione ESC para jogar novamente..."

    INFO_COR = "white"
    PERDEU_COR = "red"

    running = True
    pause = False
    fim = False
    chances = 3
    status = JogoStatus.JOGANDO

    tabuleiro_x = 0
    tabuleiro_y = 0
    tabuleiro_w = 0
    tabuleiro_h = 0

    tabuleiro_borda = 25

    bolinha_x = 0
    bolinha_y = 0
    bolinha_raio = 30
    bolinha_inc = 1
    bolinha_angulo = 0
    bolinha_alteracao_angulo = math.pi / 12

    raquete_x = 0
    raquete_y = 0
    raquete_largura = 150
    raquete_altura = 0
    raquete_move_inc = 1
    raquete_ativada = True
    raquete_movimento_tipo = RaqueteMovimentoTipo.PARADA

    dim = 0

    quadrado_borda = 1
    quadrado_w = 0
    quadrado_h = 0
    quant_quads_na_vertical = 5

    quadrados = []

    mensagem = ""
    mensagem_cor = "white"
    show_message_flag = False

    def __init__( self, screen, messageFont, chancesFont, dim ):           
        self.screen = screen
        self.messageFont = messageFont
        self.chancesFont = chancesFont

        [screen_w, screen_h] = screen.get_size()

        self.tabuleiro_x = self.tabuleiro_borda
        self.tabuleiro_y = self.tabuleiro_borda
        self.tabuleiro_w = screen_w - 2*self.tabuleiro_borda
        self.tabuleiro_h = screen_h - 2*self.tabuleiro_borda

        self.dim = dim
        self.quadrado_w = self.tabuleiro_w / self.dim
        self.quadrado_h = self.tabuleiro_h / self.dim

        self.bolinha_raio = self.quadrado_h * 3 / 4
        
        self.raquete_altura = self.quadrado_h

        self.init()

    def init( self ):
        self.moving = False
        self.running = True
        self.fim = False
        self.pause = False

        self.chances = 10
        self.status = JogoStatus.JOGANDO

        self.quadrados = []

        for i in range(0, self.quant_quads_na_vertical):
            self.quadrados.append( [0] * self.dim )
            for j in range(0, self.dim):
                if ( i < 2 or j < 2 or j > self.dim-3 or j == 4 or j == self.dim-5 ):
                    self.quadrados[ i ][ j ] = False
                else:
                    self.quadrados[ i ][ j ] = True        

        self.raquete_x = self.quadrado_w * 10
        self.raquete_y = self.tabuleiro_h - ( self.tabuleiro_h % self.quadrado_h ) - self.raquete_altura

        self.raquete_y -= 5*self.quadrado_h

        self.bolinha_x = 300
        self.bolinha_y = 200

        self.bolinha_angulo = math.pi * 3 / 2 - 1

        self.raquete_ativada = True
        self.raquete_movimento_tipo = RaqueteMovimentoTipo.PARADA

        self.show_message_flag = False
        self.mensagem_it_corrente = 0
        self.mensagem_it_tempo = 0

        self.ganhou_ou_perdeu_flag = False

    def exec_it( self ):  
        bolinha_presa = self.verifica_se_bolinha_presa()
        if ( bolinha_presa == False ):
            self.move_bolinha()

        if ( self.raquete_movimento_tipo == RaqueteMovimentoTipo.ESQUERDA ):
            self.move_raquete_para_esquerda()
        elif ( self.raquete_movimento_tipo == RaqueteMovimentoTipo.DIREITA ):
            self.move_raquete_para_direita()

        colisao_embaixo = self.verifica_e_trata_colisao_com_paredes()
        if ( colisao_embaixo == True ):
            self.chances-=1

        if ( self.chances > 0 and bolinha_presa == False ):
            self.verifica_e_trata_colisao_com_raquete()
            self.verifica_e_trata_colisao_com_quadradinho() 

        if ( self.chances == 0 ):
            if ( self.status == JogoStatus.JOGANDO ):
                self.status = JogoStatus.PERDEU
                self.mostra_mensagem( self.PERDEU, self.PERDEU_COR )           
                self.running = False
        elif ( self.conta_quadradinhos() == 0 ):
            if ( self.status == JogoStatus.JOGANDO ):
                self.status = JogoStatus.GANHOU
                self.mostra_mensagem( self.GANHOU, self.INFO_COR )           
                self.running = False            
        
    def conta_quadradinhos( self ):
        cont = 0
        for quad_list in self.quadrados:
            for quad in quad_list:
                if ( quad == True ):
                    cont+=1
        return cont
    
    def verifica_se_bolinha_presa( self ):
        bx1 = self.bolinha_x - self.bolinha_raio
        by1 = self.bolinha_y - self.bolinha_raio
        bx2 = self.bolinha_x + self.bolinha_raio
        by2 = self.bolinha_y + self.bolinha_raio
        braio = self.bolinha_raio        

        rx = self.raquete_x
        ry = self.raquete_y
        rw = self.raquete_largura
        rh = self.raquete_altura

        rx1 = rx
        ry1 = ry
        rx2 = rx + rw
        ry2 = ry + rh

        tw = self.tabuleiro_w

        return ( ( ( by1 >= ry1 and by1 < ry2 ) or ( by2 >= ry1 and by2 < ry2 ) ) and
                ( ( rx1 < 2*braio and bx2 < 2*braio ) or ( rx2 > tw-2*braio and bx1 > tw-2*braio ) ) )


    def verifica_e_trata_colisao_com_raquete( self ):
        bx1 = self.bolinha_x - self.bolinha_raio
        by1 = self.bolinha_y - self.bolinha_raio
        bx2 = self.bolinha_x + self.bolinha_raio
        by2 = self.bolinha_y + self.bolinha_raio
        bx = self.bolinha_x
        
        rx = self.raquete_x
        ry = self.raquete_y
        rw = self.raquete_largura
        rh = self.raquete_altura

        rx1 = rx
        ry1 = ry
        rx2 = rx + rw
        ry2 = ry + rh
       
        if ( self.raquete_ativada == True ):                                                   
            houve_colisao = self.houve_colisao( bx1, by1, bx2, by2, rx1, ry1, rx2, ry2 )
                            
            if ( houve_colisao == True ):                 
                pontos = [ [bx1, by1], [bx1, by2], [bx2, by1], [bx2, by2] ]     
                x, y = self.calcula_ponto_mais_proximo( pontos, (rx1+rx2)/2, (ry1+ry2)/2 )

                colidiu_com_bico = self.trata_se_houver_colisao_com_bico( x, y, rx1, ry1, rx2, ry2 )
                
                if ( colidiu_com_bico == True ):
                    self.raquete_ativada = False
                else:
                    colisao_tipo = self.calcula_raquete_colisao_tipo( bx1, by1, bx2, by2, rx1, ry1, rx2, ry2 )                                                        
                    self.ajusta_angulo_apos_colisao( colisao_tipo )                                   
                    self.raquete_ativada = False
                    
                    if ( ColisaoTipo.BAIXO ):
                        if ( bx >= rx and bx <= rx+(rw/3) ):
                            if ( self.bolinha_angulo > math.pi + math.pi/6 ):
                                self.bolinha_angulo = self.to0x360( self.bolinha_angulo - self.bolinha_alteracao_angulo )
                        elif ( bx >= rx+(rw*2/3) and bx <= rx+rw ):
                            if ( self.bolinha_angulo < math.pi + math.pi*5/6 ):
                                self.bolinha_angulo = self.to0x360( self.bolinha_angulo + self.bolinha_alteracao_angulo )                        



    def calcula_raquete_colisao_tipo( self, bx1, by1, bx2, by2, rx1, ry1, rx2, ry2 ):
        x1 = ( bx1 + bx2 ) / 2
        y1 = ( by1 + by2 ) / 2

        rcx = ( rx1 + rx2 ) / 2
        rcy = ( ry1 + ry2 ) / 2

        pontos = [ [ bx1, by1 ], [ bx1, by2 ], [ bx2, by1 ], [ bx2, by2 ] ]
        x2, y2 = self.calcula_ponto_mais_proximo( pontos, rcx, rcy )

        esq_x = rx1
        esq_y = self.calcula_y( esq_x, x1, y1, x2, y2 )

        dir_x = rx2
        dir_y = self.calcula_y( dir_x, x1, y1, x2, y2 )

        if ( self.bolinha_angulo >= 0 and self.bolinha_angulo <= math.pi/2 ):
            if ( esq_y >= ry1 and esq_y <= ry2 ):
                return ColisaoTipo.FRENTE
            else: return ColisaoTipo.BAIXO
        elif ( self.bolinha_angulo >= math.pi/2 and self.bolinha_angulo <= math.pi ):
            if ( dir_y >= ry1 and dir_y <= ry2 ):
                return ColisaoTipo.TRAZ
            else: return ColisaoTipo.BAIXO
        elif ( self.bolinha_angulo >= math.pi and self.bolinha_angulo <= math.pi*3/2 ):
            if ( dir_y >= ry1 and dir_y <= ry2 ):
                return ColisaoTipo.TRAZ
            else: return ColisaoTipo.CIMA
        elif ( self.bolinha_angulo >= math.pi*3/2 and self.bolinha_angulo < 2*math.pi ):
            if ( esq_y >= ry1 and esq_y <= ry2 ):
                return ColisaoTipo.FRENTE
            else: return ColisaoTipo.CIMA



    def verifica_e_trata_colisao_com_quadradinho( self ):
        bx1 = self.bolinha_x - self.bolinha_raio
        by1 = self.bolinha_y - self.bolinha_raio
        bx2 = self.bolinha_x + self.bolinha_raio
        by2 = self.bolinha_y + self.bolinha_raio

        pontos = [ [bx1, by1], [bx1, by2], [bx2, by1], [bx2, by2] ]
        i = 0
        colidiu = False
        while ( i < len( pontos ) and colidiu == False ):
            x = pontos[i][0]
            y = pontos[i][1]
            nqx = int( x / self.quadrado_w )
            nqy = int( y / self.quadrado_h )
           
            if ( nqx >= 0 and nqx < self.dim and nqy >= 0 and nqy < self.quant_quads_na_vertical ):
                ativo = self.quadrados[ nqy ][ nqx ]
                if ( ativo ):
                    self.quadrados[ nqy ][ nqx ] = False

                    qx = nqx * self.quadrado_w
                    qy = nqy * self.quadrado_h
                    qw = self.quadrado_w
                    qh = self.quadrado_h

                    qx1 = qx
                    qy1 = qy
                    qx2 = qx+qw
                    qy2 = qy+qh

                    colisao_tipo = self.calcula_quadradinho_colisao_tipo( x, y, qx1, qy1, qx2, qy2 )                    
                    self.ajusta_angulo_apos_colisao( colisao_tipo )

                    self.raquete_ativada = True
                    colidiu = True
            i+=1        
        

    def calcula_quadradinho_colisao_tipo( self, x, y, x1, y1, x2, y2 ):
        dx1 = self.abs( x - x1 )
        dx2 = self.abs( x - x2 )
        dy1 = self.abs( y - y1 )
        dy2 = self.abs( y - y2 )

        dists = [ dx1, dx2, dy1, dy2 ]
        colisoes_tipos = [ ColisaoTipo.FRENTE, ColisaoTipo.TRAZ, ColisaoTipo.BAIXO, ColisaoTipo.CIMA ]

        j = 0
        min = 9999999
        for i in range( 0, len( dists ) ):
            if ( dists[ i ] < min ):                
                j = i
                min = dists[ i ]

        return colisoes_tipos[ j ]
    

    def trata_se_houver_colisao_com_bico( self, x, y, rx1, ry1, rx2, ry2 ):       
        pontos = [ [rx1, ry1], [rx1, ry2], [rx2, ry1], [rx2, ry2] ]
        verificacoes = [
            self.bolinha_angulo >= 0 and self.bolinha_angulo < math.pi/2,           # quadrante 1           
            self.bolinha_angulo >= math.pi*3/2 and self.bolinha_angulo < 2*math.pi, # quadrante 4
            self.bolinha_angulo >= math.pi/2 and self.bolinha_angulo < math.pi,     # quadrante 2
            self.bolinha_angulo >= math.pi and self.bolinha_angulo < math.pi*3/2    # quadrante 3
        ]

        j = 0
        min_dist = 9999999
        for i in range( 0, len( pontos ) ):
            dist = math.sqrt( math.pow( x - pontos[ i ][ 0 ], 2 ) + math.pow( y - pontos[ i ][ 1 ], 2 ) )
            if ( dist < min_dist ):
                j = i
                min_dist = dist
        
        if ( rx2-rx1 < ry2-ry1 ):
            rdist = rx2-rx1
        else: rdist = ry2-ry1

        if ( min_dist <= rdist/4 ):
            if ( verificacoes[ j ] == True ):
                self.bolinha_angulo = self.to0x360( self.bolinha_angulo + math.pi )
                return True
           
        return False                


    def houve_colisao( self, x1, y1, x2, y2, x3, y3, x4, y4 ):
        pontos1 = [ [ x1, y1 ], [ x1, y2 ], [ x2, y1 ], [ x2, y2 ] ]
        pontos2 = [ [ x3, y3 ], [ x3, y4 ], [ x4, y3 ], [ x4, y4 ] ]

        xc = ( x3 + x4 ) / 2
        yc = ( y3 + y4 ) / 2

        x, y = self.calcula_ponto_mais_proximo( pontos1, xc, yc )

        if ( x >= x3 and x <= x4 and y >= y3 and y <= y4 ):
            return True
        else:
            xc = ( x1 + x2 ) / 2
            yc = ( y1 + y2 ) / 2
            
            x, y = self.calcula_ponto_mais_proximo( pontos2, xc, yc )

            if ( x >= x1 and x <= x2 and y >= y1 and y <= y2 ):
                return True
        
        return False
    

    def calcula_ponto_mais_proximo( self, pontos, rcx, rcy ):
        j = 0
        min = 9999999
        for i in range( 0, len( pontos ) ):
            dist = math.sqrt( math.pow( rcx - pontos[ i ][ 0 ], 2 ) + math.pow( rcy - pontos[ i ][ 1 ], 2 ) )
            if ( dist < min ):
                j = i
                min = dist

        return pontos[ j ][ 0 ], pontos[ j ][ 1 ]


    def calcula_y( self, x, x1, y1, x2, y2 ):
        if ( x1 == x2 ):
            if ( y1 < y2 ):
                return y1
            return y2
        else: 
            cang = (y2-y1)/(x2-x1)
            return cang * ( x-x1 ) + y1
        
    def calcula_x( self, y, x1, y1, x2, y2 ):
        if ( x1 == x2 ):
            return x1
        else: 
            cang = (y2-y1)/(x2-x1)
            return ( y - y1 + cang*x1 ) / cang
    
    def verifica_e_trata_colisao_com_paredes( self ):
        if ( self.bolinha_x - self.bolinha_raio < 0 ):
            self.ajusta_angulo_apos_colisao( ColisaoTipo.TRAZ )
            self.raquete_ativada = True
        elif ( self.bolinha_x + self.bolinha_raio > self.tabuleiro_w ):
            self.ajusta_angulo_apos_colisao( ColisaoTipo.FRENTE )
            self.raquete_ativada = True

        if ( self.bolinha_y - self.bolinha_raio < 0 ):
            self.ajusta_angulo_apos_colisao( ColisaoTipo.CIMA )
            self.raquete_ativada = True
        elif( self.bolinha_y + self.bolinha_raio > self.tabuleiro_h ):            
            if ( self.chances > 1 ):
                self.ajusta_angulo_apos_colisao( ColisaoTipo.BAIXO )
                self.raquete_ativada = True                
            else:
                self.running = False                         
            return True
    
        return False
        

    def ajusta_angulo_apos_colisao(self, colisao_tipo):
        if ( colisao_tipo == ColisaoTipo.TRAZ ):
            if ( self.bolinha_angulo > math.pi / 2 and self.bolinha_angulo < math.pi ):
                self.bolinha_angulo = ( math.pi / 2 ) - ( self.bolinha_angulo - ( math.pi / 2 ) )
            else: self.bolinha_angulo = ( math.pi * 3 / 2 ) + ( ( math.pi * 3 / 2 ) - self.bolinha_angulo )
        elif ( colisao_tipo == ColisaoTipo.FRENTE ):           
            if ( self.bolinha_angulo > (math.pi * 3 / 2) and self.bolinha_angulo < 2*math.pi ):
                self.bolinha_angulo = math.pi + ( ( 2 * math.pi ) - self.bolinha_angulo )
            else: self.bolinha_angulo = math.pi - self.bolinha_angulo
        elif ( colisao_tipo == ColisaoTipo.CIMA ):
            if ( self.bolinha_angulo > (math.pi * 3 / 2) and self.bolinha_angulo < 2*math.pi ):
                self.bolinha_angulo = ( 2*math.pi - self.bolinha_angulo )
            else: self.bolinha_angulo =  ( math.pi / 2 ) + ( ( math.pi * 3 / 2 ) - self.bolinha_angulo )
        elif ( colisao_tipo == ColisaoTipo.BAIXO ):
            if ( self.bolinha_angulo > (math.pi / 2) and self.bolinha_angulo < math.pi ):
                self.bolinha_angulo = ( math.pi * 3 / 2 ) - ( self.bolinha_angulo - math.pi / 2 )
            else: self.bolinha_angulo = ( 2 * math.pi ) - ( self.bolinha_angulo )


    def move_bolinha( self ):
        self.bolinha_x += self.bolinha_inc * math.cos( self.bolinha_angulo )
        self.bolinha_y += self.bolinha_inc * math.sin( self.bolinha_angulo )                   

    def move_raquete_para_esquerda( self ):
        self.move_raquete( -self.raquete_move_inc )

    def move_raquete_para_direita( self ):
        self.move_raquete( self.raquete_move_inc )

    def move_raquete( self, xinc ):        
        if ( self.raquete_x + xinc < 0 ):
            self.raquete_x = 0
        elif ( self.raquete_x + xinc > ( self.tabuleiro_w - self.raquete_largura ) ):
            self.raquete_x = self.tabuleiro_w - self.raquete_largura
        else:
            self.raquete_x += xinc
        
    def mostra_mensagem( self, mensagem, cor, it = 0, tempo=0 ):
        self.mensagem = mensagem
        self.mensagem_cor = cor
        self.show_message_flag = True
        self.mensagem_it_corrente = it
        self.mensagem_it_tempo = tempo

    def esconde_mensagem( self ):
        self.show_message_flag = False

    def draw_game( self ):
        self.screen.fill( 'black' )
        self.draw_quadrados()
        self.draw_raquete()
        self.draw_bolinha()
        self.draw_bordas()
        self.draw_chances()
        self.draw_mensagem()

    def draw_raquete( self ):        
        x = self.tabuleiro_x + self.raquete_x
        y = self.tabuleiro_y + self.raquete_y
        w = self.raquete_largura
        h = self.raquete_altura

        pygame.draw.rect( self.screen, 'blue', (x, y, w, h) )

    def draw_bolinha( self ):
        x = self.tabuleiro_x + self.bolinha_x
        y = self.tabuleiro_y + self.bolinha_y
        r = self.bolinha_raio        

        pygame.draw.circle( self.screen, 'green', (x, y), r )
        

    def draw_bordas( self ):
        tx = self.tabuleiro_x
        ty = self.tabuleiro_y
        tw = self.tabuleiro_w
        th = self.tabuleiro_h

        linhas = [ 
            [tx, ty+th, tx, ty], 
            [tx, ty, tx+tw, ty], 
            [tx+tw, ty, tx+tw, ty+th ],
            [tx, ty+th, tx+tw, tx+th ]
        ]
        cores = ["white", "white", "white", "yellow"]
        for i in range( 0, len( linhas )):
            lx1 = linhas[i][0]
            ly1 = linhas[i][1]
            lx2 = linhas[i][2]
            ly2 = linhas[i][3]

            pygame.draw.line( self.screen, cores[i], (lx1, ly1), (lx2, ly2), 1 )

    def draw_quadrados( self ):              
        tx = self.tabuleiro_x
        ty = self.tabuleiro_y
        
        for j in range(0, self.dim):
            for i in range(0, self.quant_quads_na_vertical):
                if ( self.quadrados[ i ][ j ] == False ):
                    continue

                qx = tx + j * self.quadrado_w
                qy = ty + i * self.quadrado_h
                qw = self.quadrado_w
                qh = self.quadrado_h

                x = tx + j * qw + self.quadrado_borda
                y = ty + i * qh + self.quadrado_borda
                w = qw - ( 2 * self.quadrado_borda )
                h = qh - ( 2 * self.quadrado_borda )                

                pygame.draw.rect( self.screen, 'black', (qx, qy, qw, qh), 1, 1 )
                pygame.draw.rect( self.screen, 'blue', (x, y, w, h) )        

    def draw_chances( self ):
        img = chancesFont.render( str( self.chances ), True, "white" )
        rect = img.get_rect()

        tx = self.tabuleiro_x + ( self.tabuleiro_w - rect.width - 10 )
        ty = self.tabuleiro_y + ( self.tabuleiro_h - rect.height - 10 )

        screen.blit( img, (tx, ty) )

    def draw_mensagem( self ):
        if ( self.show_message_flag == True ):
            img = messageFont.render( self.mensagem, True, self.mensagem_cor )
            rect = img.get_rect()

            tx = self.tabuleiro_x + ( ( self.tabuleiro_w - rect.width ) / 2 )
            ty = self.tabuleiro_y + ( ( self.tabuleiro_h - rect.height ) / 2 )

            screen.blit( img, (tx, ty) )


    def to0x360( self, ang ):
        if ( ang >= 0 ):
            return ang % (2*math.pi)
        else: 
            return (2*math.pi) - ( -ang % (2*math.pi) )

    def toDegree( self, ang ):
        return ang / math.pi * 180

    def abs( self, valor ):
        if valor < 0:
            return -valor
        else: return valor

    def executaPausa( self ):
        if ( self.running ):
            self.pause = not self.pause
            if ( self.pause == True ):
                self.mostra_mensagem( self.PAUSE, self.INFO_COR )
            else: self.esconde_mensagem()

    def isFim( self ):
        return self.fim

    def isRunning( self ):
        return self.running

    def isJogando( self ):
        return self.running and self.isFim() == False and self.pause == False
        
    def isMoving( self ):
        return self.raquete_movimento_tipo != RaqueteMovimentoTipo.PARADA and self.isJogando()

    def setRaqueteMovimentoTipo( self, movimento_tipo ):
        self.raquete_movimento_tipo = movimento_tipo

    def setRunning( self, running ):
        self.running = running

    def setFim( self, fim ):
        self.fim = fim

pygame.init()
screen = pygame.display.set_mode( (640, 480) )
clock = pygame.time.Clock()
messageFont = pygame.font.SysFont( None, 30 )
chancesFont = pygame.font.SysFont( None, 45 )

game = Game( screen, messageFont, chancesFont, 20 )

it_mult = 10
it = 0

while game.fim == False:
    if ( game.isJogando() ):
        game.exec_it()
        
    for event in pygame.event.get(): 
        if ( event.type == pygame.QUIT ):
            game.setFim( True )        
        elif ( event.type == pygame.KEYDOWN ):
            if ( event.key == pygame.K_ESCAPE ):
                game.init()
            elif ( event.key == pygame.K_RETURN ):
                game.executaPausa()                

            if ( game.isJogando() ):                
                if ( event.key == pygame.K_LEFT ):
                    game.setRaqueteMovimentoTipo( RaqueteMovimentoTipo.ESQUERDA )
                elif ( event.key == pygame.K_RIGHT ):
                    game.setRaqueteMovimentoTipo( RaqueteMovimentoTipo.DIREITA )                
        elif ( event.type == pygame.KEYUP ):
            if ( game.isJogando() ):
                if ( event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT ):
                    game.setRaqueteMovimentoTipo( RaqueteMovimentoTipo.PARADA )

    it+=1
    if ( it % it_mult == 0 ):
        game.draw_game()
        pygame.display.flip()

        clock.tick( 30 )

pygame.quit()