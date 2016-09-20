#!/usr/bin/env python3
# Criado por Dyego (dyegomb.wordpress.com)
#
import os, taglib, pickle, sqlite3
from hashlib import md5
from datetime import datetime


class DadosMp3(object):
    """Gera e coleta dados de arquivos mp3"""

    def __init__(self, localMp3):
        self.localMp3 = os.path.abspath(localMp3)
        self.localHost = os.uname().nodename
        self.dataAnalise = datetime.now()
        self.basename = os.path.basename(localMp3)
        try:
            self.hash = self.geraHash(self.localMp3)
        except Exception as e:
            print("ERRO ao gerar md5 hash para o arquivo:", self.localMp3, e)
            raise IOError

        try:
            self.coletarDados(self.localMp3)
        except Exception as erro:
            print("Erro ao coletar dados da TAG:", erro)

        self.bytes = os.path.getsize(self.localMp3)

    def __repr__(self):
        """Retorna informações do mp3 em JSON"""
        data = str(self.dataAnalise[2]) + "/" + str(self.dataAnalise[1]) + "/" + str(self.dataAnalise[0])
        jsonDados = str("[{'artista':'" + self.artista + "'}," +
                        "{'album':'" + self.album + "'}," +
                        "{'hash':'" + self.hash + "'}," +
                        "{'bytes':'" + str(self.bytes) + "'}," +
                        "{'data de analise':'" + data + "'}]")
        return str(jsonDados)

    def coletarDados(self, localMp3):
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
            self.allTags = dados.tags
        except Exception:
            pass

    @staticmethod
    def geraHash(localMp3):
        try:
            calculador = md5()
            with open(localMp3, "rb") as arqMp3:
                # for parte in iter(partial(arqMp3.read, 4096), b''):
                while True:
                    parte = arqMp3.read(4096)
                    if not parte: break

                    calculador.update(parte)

            return calculador.hexdigest()

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


def duplicado(dbCursor, dbTable, valor, coluna, colunaConsulta="",
              mostrarValores=False):
    """Retorna valor booleano na verificação de valor já existente."""

    if colunaConsulta == "": colunaConsulta = coluna

    sql = str('select "' + coluna + '" from "' + dbTable + '" where "' +
              colunaConsulta + '" = "' + valor + '"')

    try:
        resultado = dbCursor.execute(sql)
        if mostrarValores:
            return resultado.fetchall()
        else:
            if resultado.fetchone():
                return True
            else:
                return False

    except Exception as e:
        print("Erro em consulta:", sql, [coluna, colunaConsulta, valor], "//", e)
        raise RuntimeError

def menuComparar():
    # Analisar por hash, comparar artista e musica (trazer album tamanho, etc.)
    # verificar index?
    pass

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
                pickleMp3 = pickle.dumps(dadosMp3)
            except Exception as e:
                print("Erro ao analisar", mp3, "//", e)
                erroNum += 1
                if [[ erroNum >= 5 ]]:
                    print("ERRO(1): Muitos erros durante análise. Processo abortado.")
                    raise RuntimeError

            try:
                sql = ""
                if duplicado(dbcursor, tbComputador, dadosMp3.localMp3, "arquivo"):
                    if not sobreescreverTodos:
                        print("")
                        qstSobreescrever = questionar(str("Arquivo " + str(mp3) + " já existente no banco, " +
                                                          "sobreescrever informações?"))
                        if qstSobreescrever:
                            sobreescreverTodos = questionar("Sobreescrever em todos duplicados?")
                        else:
                            print("Análise interrompida.")
                            break

                    if sobreescreverTodos or qstSobreescrever:
                        sql = str('UPDATE "' + tbComputador + '" SET arquivo = ?, basename = ?, hash = ?, ' +
                                  'tamanho = ?, dataAnalise = ?, artista = ?, musica = ?, objeto = ? ' +
                                  'WHERE "arquivo" = "' + dadosMp3.localMp3 + '"')
                if not sql:
                    sql = str('insert into "' + tbComputador + '"(arquivo, basename, hash, ' +
                              "tamanho, dataAnalise, artista, musica, objeto)" +
                              " values (?, ?, ?, ?, ?, ?, ?, ?)")

                sqlValues = [dadosMp3.localMp3, dadosMp3.basename, dadosMp3.hash,
                             dadosMp3.bytes, dadosMp3.dataAnalise, dadosMp3.artista,
                             dadosMp3.titulo, pickleMp3]

                dbcursor.execute(sql, sqlValues)

                if [[loopCommit >= 50 | i >= qntMp3s]]:
                    conexaodb.commit()
                    loopCommit = 0
            except Exception as e:
                print("Erro ao gravar informações em banco de", dadosMp3.localMp3, "//", e)
                erroNum += 1
                if [[ erroNum >= 5 ]]:
                    print("ERRO(2): Muitos erros(", erroNum, ") durante análise. Processo abortado.")
                    raise RuntimeError

def main(banco=sqlite3.connect("dados.db")):
    dbcursor = banco.cursor()
    tbComputador = str(os.uname().nodename + "_v1.0")

    sql = str('CREATE TABLE if not exists "' + tbComputador +
              '"(arquivo TEXT, basename TEXT, hash TEXT, tamanho INT,' +
              'dataAnalise DATE, artista TEXT, musica TEXT, objeto BLOB)')

    dbcursor.execute(sql)
    conexaodb.commit()
    
    if [[ len(sys.argv) >= 2 ]]:
        localVarrer = os.path.abspath(sys.argv[-1])
        qstVarrerDir = True
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        localVarrer = ""
        qstVarrerDir = questionar("Realizar varredura de \
diretorio?")
        qstCompararPCs = questionar("Comparar dados de computadores diferentes?")

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
        pass





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
