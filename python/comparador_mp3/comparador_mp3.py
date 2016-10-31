#!/usr/bin/env python3
#
# Criado por Dyego (dyegomb.wordpress.com)
#
import os
import taglib
#import pickle
import sqlite3
from acoustid import fingerprint_file
#from hashlib import md5
from datetime import datetime


class DadosMp3(object):
    """Gera e coleta dados de arquivos mp3 ou banco SQLite"""

    def __init__(self, localMp3):
        if type(localMp3) == str and os.path.isfile(localMp3):
            self.arquivo = os.path.abspath(localMp3)
            self.localHost = os.uname().nodename
            self.dataAnalise = datetime.now()
            self.basename = os.path.basename(localMp3)
            self.dataModificado = datetime.fromtimestamp(os.path.getmtime(localMp3))
            try:
                self.duracao, self.fingerprint = self.geraFingerprint(self.arquivo)
            except Exception as e:
                print("ERRO ao gerar fingerprint para o arquivo:", self.arquivo,
                      e)
                raise IOError

            self.tamanho = os.path.getsize(self.arquivo)

            # Capturar informações da TAG
            dados = taglib.File(localMp3)
            try:
                self.artista = dados.tags['ARTIST'][0]
            except KeyError:
                self.artista = "DESCONHECIDO"
            try:
                self.album = dados.tags['ALBUM'][0]
            except KeyError:
                self.album = "DESCONHECIDO"
            try:
                self.titulo = dados.tags['TITLE'][0]
            except KeyError:
                self.titulo = "DESCONHECIDO"
            try:
                self.tags = str(dados.tags)
            except Exception:
                self.tags = ""

        elif type(localMp3) is sqlite3.Cursor:
        #else:
            #http://stackoverflow.com/questions/2466191/set-attributes-from-dictionary-in-python
            try:
                for coluna, dado in zip(localMp3.description, localMp3.fetchone()):
                    setattr(self, coluna[0], dado)

                resultado = localMp3.execute("select name from sqlite_master")
                nometabela = resultado.fetchone()[0]
                remover = str("_"+nometabela.split("_")[-1])
                self.localHost = nometabela.strip(remover)

            except Exception as e:
                print("ERRO durante \"parse\" em select :", e)
                raise EOFError
        else:
            print("Objeto", localMp3, "não pode ser inicializado.")
            raise EOFError

        self.lista = [self.artista, self.titulo, self.album,
                      self.dataAnalise, self.tamanho, self.fingerprint]
        self.index = len(self.lista)


    def __iter__(self):
        # return self # executa o loop for apenas uma vez
        return iter(self.lista)

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.lista[self.index]

    def __getitem__(self, key):
        dicionario = {'artista': self.artista, 'título': self.titulo,
                      'albúm': self.album, 'fingerprint': self.fingerprint, 'tamanho': self.bytes}
        return dicionario[key]
        # return self.lista[index]

    def __repr__(self):
        """Retorna informações do mp3 em JSON"""
        data = str(self.dataAnalise[2]) + "/" + str(self.dataAnalise[1]) + "/" + str(self.dataAnalise[0])
        jsonDados = str("[{'artista':'" + self.artista + "'}," +
                        "{'album':'" + self.album + "'}," +
                        "{'fingerprint':'" + self.fingerprint + "'}," +
                        "{'bytes':'" + str(self.tamanho) + "'}," +
                        "{'data de analise':'" + data + "'}]")
        return str(jsonDados)

    @staticmethod
    def geraFingerprint(localMp3):
        try:
            #calculador = md5()
            #with open(localMp3, "rb") as arqMp3:
            #    # for parte in iter(partial(arqMp3.read, 4096), b''):
            #    while True:
            #        parte = arqMp3.read(4096)
            #        if not parte: break
            #
            #        calculador.update(parte)
            #
            #return calculador.hexdigest()
            arqTempoFingerprint = fingerprint_file(localMp3)
            return arqTempoFingerprint

        except IOError:
            print("ERRO ao abrir arquivo:", localMp3)
            raise IOError


def varrerDir(inicialDir='.', extensao='.mp3'):
    """Varre diretório recursivamente a procura de arquivo com
extensão solicitada e gera uma lista"""
    listaArquivos = list()
    for pasta, _, _ in os.walk(inicialDir):
        for arquivo in os.listdir(pasta):
            arquivoFull = os.path.abspath(pasta + "/" + arquivo)
            if os.path.isfile(arquivoFull):
                if arquivo.lower().endswith(extensao):
                    listaArquivos.append(arquivoFull)
    return listaArquivos


def questionar(questao=""):
    retorno = input(str(questao + " (S/N):"))
    if retorno.upper()[0] == "S":
        return True
    else:
        return False


# noinspection PyTypeChecker
def duplicado(dbCursor, dbTable, valor, coluna, colunaConsulta="",
              mostrarValores=False, dbTable2="", seJaExistente=False):
    """Retorna valor booleano na verificação de valor já existente."""

    if colunaConsulta == "": colunaConsulta = coluna

    if dbTable == dbTable2 and dbTable != "":
        sql = str('select "' + coluna + '", ROWID from "' + dbTable + '" where "' +
                  colunaConsulta + '" = "' + valor + '"')
    else:
        sql = str('select "' + coluna + '", ROWID from "' + dbTable + '" where "' +
                  colunaConsulta + '" = "' + valor + '"')
    # Como pegar tb o ROWID ??

    dir(sql)

    if dbTable2:
        sql2 = str('select "' + coluna + '", ROWID from "' + dbTable2 + '" where "' +
                   colunaConsulta + '" = "' + valor + '"')
    else:
        sql2 = False

    try:
        resultado = dbCursor.execute(sql)
        if sql2:
            resultado2 = dbCursor.execute(sql2)
        else: resultado2 = False

        if mostrarValores:
            return resultado.fetchall()
        else:
            if seJaExistente:
                if resultado.fetchone(): return True
            elif resultado.fetchone() == resultado2.fetchone():
                return True
            else:
                return False

    except Exception as e:
        print("Erro em consulta:", sql, [coluna, colunaConsulta, valor], "//", e)
        raise RuntimeError


def menuComparar():
    # Analisar por fingerprint, comparar artista e musica (trazer album tamanho, etc.)
    # verificar index?
    dicOpts = {1:"Verificar fingerprints duplicados em mesma tabela",
               2:"Verificar fingerprints duplicados em tabelas diferentes",
               3:"Verificar mp3 com Artista e Música duplicados em mesma tabela",
               4:"Verificar mp3 com Artista e Música duplicados tabelas diferentes"}
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("====== Comparações ======")
        for i in dicOpts.keys():
            print(i, "-", dicOpts[i])
        print("0 - Sair")
        sys.stdout.write("Opção: ")

        try:
            opcao = int(input())
            if int(opcao) in dicOpts.keys():
                return int(opcao)
            elif opcao in ["0", 0]:
                break
            else:
                print("Opção indisponível. Tente novamente.")
                continue
        except ValueError:
            print ("Opção inválida!")
            continue


def acaoVarrer(dbCursor, localVarrer, tbComputador):
    dbcursor = dbCursor
    listaMp3s = varrerDir(localVarrer)
    qntMp3s = len(listaMp3s)
    qstAnalise = questionar(str("Serão analisados " + str(qntMp3s) + " arquivos, continuar?"))
    sobreescreverTodos = False

    if qstAnalise:
        i = 0
        loopCommit = 0
        erroNum = 0
        for mp3 in listaMp3s:
            i += 1
            loopCommit += 1
            sys.stdout.write('\r')
            sys.stdout.write(str("Analisando " + str(i) + "/" +
                                 str(qntMp3s)))
            sys.stdout.flush()

            try:
                dadosMp3 = DadosMp3(mp3)
                #pickleMp3 = pickle.dumps(dadosMp3)
            except Exception as e:
                dadosMp3 = DadosMp3(mp3)
                print("Erro ao analisar", mp3, "//", e)
                erroNum += 1
                pickleMp3 = ""
                if erroNum >= 5:
                    print("ERRO(1): Muitos erros durante análise. Processo abortado.")
                    raise RuntimeError

            try:
                sql = ""
                if duplicado(dbcursor, tbComputador, dadosMp3.arquivo, "arquivo", seJaExistente=True):
                    qstSobreescrever = False
                    if not sobreescreverTodos:
                        print("")
                        qstSobreescrever = questionar(str("Arquivo " + str(mp3) + " já existente no banco, " +
                                                          "sobreescrever informações?"))
                        if qstSobreescrever:
                            sobreescreverTodos = questionar("Sobreescrever em todos duplicados?")
                            # else:
                            #    print("Análise interrompida.")
                            #    break

                    if sobreescreverTodos or qstSobreescrever:
                        sql = str('UPDATE "' + tbComputador + '" SET arquivo = ?, basename = ?, '+
                              'dataAnalise = ?, dataModificado = ?, duracao = ?, fingerprint = ?, '+
                              'artista = ?, titulo = ?, tamanho = ?, album = ?, tags = ?' +
                                  'WHERE "arquivo" = "' + dadosMp3.arquivo + '"')
                if not sql:
                    sql = str('insert into "' + tbComputador + '"(arquivo, basename, '+
                              'dataAnalise, dataModificado, duracao, fingerprint, '+
                              'artista, titulo, tamanho, album, tags)' +
                              ' values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')

                sqlValues = [dadosMp3.arquivo, dadosMp3.basename, dadosMp3.dataAnalise,
                             dadosMp3.dataModificado, dadosMp3.duracao, dadosMp3.fingerprint,
                             dadosMp3.artista, dadosMp3.titulo, dadosMp3.tamanho,
                             dadosMp3.album, dadosMp3.tags ]

                dbcursor.execute(sql, sqlValues)

                if loopCommit >= 50 or i >= qntMp3s:
                    conexaodb.commit()
                    loopCommit = 0
            except Exception as e:
                print("Erro ao gravar informações em banco de", dadosMp3.arquivo, "//", e)
                erroNum += 1
                if erroNum >= 5:
                    print("ERRO(2): Muitos erros(", erroNum, ") durante análise. Processo abortado.")
                    print(sql, sqlValues)
                    raise RuntimeError
        print("")


def main(banco=sqlite3.connect("dados.db")):
    dbcursor = banco.cursor()
    versao = "_v1.0"
    tbComputador = str(os.uname().nodename + versao)

    sql = str('CREATE TABLE if not exists "' + tbComputador +
              '"(arquivo TEXT, basename TEXT, dataAnalise DATE, dataModificado DATE, duracao REAL, '+
              'fingerprint TEXT, artista TEXT, titulo TEXT, tamanho INT, album TEXT, tags TEXT)')
              #'"(arquivo TEXT, basename TEXT, fingerprint TEXT, tamanho INT,' +
              #'dataAnalise DATE, dataModificado DATE, artista TEXT, musica TEXT)')

    dbcursor.execute(sql)
    conexaodb.commit()

    if len(sys.argv) >= 2:
        localVarrer = os.path.abspath(sys.argv[-1])
        qstVarrerDir = True
        qstCompararPCs = False
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        localVarrer = ""
        qstVarrerDir = questionar("Realizar varredura de diretorio?")
        qstCompararPCs = questionar("Comparar dados de tabelas diferentes?")

    if qstVarrerDir:
        while (not os.path.isdir(localVarrer) and not
        os.path.exists(localVarrer)) or localVarrer == "":
            try:
                localVarrer = os.path.abspath(
                    input("Diretório para realizar a \
varredura de arquivos .mp3: "))
                if os.path.isdir(localVarrer):
                    break
                else:
                    raise IsADirectoryError
            except Exception as e:
                print("Diretório", localVarrer, "inválido, tente novamente. //", e)

        acaoVarrer(dbcursor, localVarrer, tbComputador)

    if qstCompararPCs:
        optComparar = menuComparar()


if __name__ == '__main__':
    import sys

    nomeBanco = input("Informe a base de dados [dados.db]:")
    if not nomeBanco:
        nomeBanco = "dados.db"
    localBanco = os.path.abspath(nomeBanco)
    conexaodb = sqlite3.connect(localBanco)
    try:
        main(conexaodb)
    finally:
        conexaodb.commit()
        conexaodb.close()


    ## Testes
    #from pydub import AudioSegment
    #tempo, fingerprint = acoustid.fingerprint_file("/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box.mp3")
    #print (tempo, len(fingerprint), fingerprint)
    #tempo2, fingerprint2 = acoustid.fingerprint_file("/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box_3.aiff")
    #print (tempo2, len(fingerprint2), fingerprint2)
    #
    #count = 0
    #igcount = 0
    #for i, a in zip(fingerprint2, fingerprint):
    #    #print (i, a)
    #    count += 1
    #    if i == a: igcount += 1
    #
    #print((igcount/count)*100)
    #
    #print(len(fingerprint),",", len(fingerprint2))
    #
    #lista = [fingerprint2[i:i + 5] for i in range(0, len(fingerprint2), 5)]
    #n=0
    #for i in lista:
    #    #print (i)
    #    if i in fingerprint:
    #        print("Deu macth", n)
    #        n += 1
    #
    #print (n, "em", len(lista), i)
    #print (n/len(lista))
    #
    #sound = AudioSegment.from_mp3("/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box_3.mp3")
    #parte = sound[30:80]
    #partes = [sound[i:i + 30] for i in range(0, len(sound), 30)]
    #print (parte.raw_data)
    ##teste = acoustid.fingerprint(partes[2], 2, partes)
    ##print(teste)
    #
    #
    ##from beets import plugins as beets

    #dbcursor = conexaodb.cursor()
    #sql = """select * from 'conab-dyego_v1.0' where rowid = 6"""
    #resultado = dbcursor.execute(sql)
    #print(type(resultado))
    #print(resultado.fetchone()[0])
    #print (dir(dbcursor.execute(sql)))
    #teste = DadosMp3(resultado)
    #print(teste.artista)
    #print(teste.localHost)
    #conexaodb.close()

    #import acoustid#, io #audioread
    #with audioread.audio_open("/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box_3.mp3") as arquivo:
    #with open("/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box.mp3",
    #          "rb") as arquivo:
    #    #parte = bytes(arquivo.read(10000)[0:220])
    #    arquivo.seek(0)
    #    fingerfull = acoustid.fingerprint(44100, 2, arquivo)
    #
    #with open("/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box_3.mp3",
    #          "rb") as arquivo2:
    #    arquivo2.read(1000000)
    #    parte1 = arquivo2.read(1000000)
    #    parte2 = arquivo2.read(1000000)
    #    if parte1 == parte2 : print("Oou")
    #    parte = io.BytesIO(arquivo2.read(1000000))
    #    finger1 = acoustid.fingerprint(44100, 2, parte)


    #tempo2, finger1 = acoustid.fingerprint_file("/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box.aiff")
    #tempo, fingerfull = acoustid.fingerprint_file(
    #    "/home/dyego/Música/Alice in Chains/(2001) Alice in Chains Greatest Hits/Alice in Chains-01-Man in the Box.mp3")
    #
    #lista = [finger1[p:p + 3] for p in range(0, len(finger1), 3)]
    #n = 0
    #for i in lista:
    #    if i in fingerfull:
    #        n += 1
    #print(n, "em", len(lista), i)
    #print(n / len(lista)*100)
    #
    #
    #if finger1 in fingerfull: print("OK")
    #print (finger1)
    #print (fingerfull)