#!/usr/bin/env python3
#
# Criado por Dyego (dyegomb.wordpress.com)
#
import os, taglib, pickle, sqlite3
from acoustid import fingerprint_file
#from hashlib import md5
from datetime import datetime


class DadosMp3(object):
    """Gera e coleta dados de arquivos mp3 ou banco SQLite"""

    def __init__(self, localMp3):
        if type(localMp3) == str and os.path.isfile(localMp3):
            self.localMp3 = os.path.abspath(localMp3)
            self.localHost = os.uname().nodename
            self.dataAnalise = datetime.now()
            self.basename = os.path.basename(localMp3)
            self.dataModificado = datetime.fromtimestamp(os.path.getmtime(localMp3))
            try:
                self.tempo, self.fingerprint = self.geraFingerprint(self.localMp3)
            except Exception as e:
                print("ERRO ao gerar fingerprint para o arquivo:", self.localMp3,
                      e)
                raise IOError

            self.bytes = os.path.getsize(self.localMp3)

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
                self.allTags = dados.tags
            except Exception:
                pass



        #elif type(localMp3) == "sqlite3.Cursor":
        else:
            #http://stackoverflow.com/questions/2466191/set-attributes-from-dictionary-in-python
            try:
                for coluna, dado in zip(localMp3.description, localMp3.fetchone()):
                    setattr(self, coluna[0], dado)
            except Exception as e:
                print("ERRO durante \"parse\" em select :", e)
                raise EOFError

        self.lista = [self.artista, self.titulo, self.album, self.fingerprint,
                      self.dataAnalise, self.localHost, self.bytes]
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
                        "{'bytes':'" + str(self.bytes) + "'}," +
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

    if not dbTable: return

    if dbTable == dbTable2:
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
    menu = """
    ====== Comparações ======

    1 - Verificar fingerprints duplicados em mesma tabela;
    2 - Verificar fingerprints duplicados em tabelas diferentes;
    3 - Verificar mp3 com Artista e Música duplicados em mesma tabela;
    4 - Verificar mp3 com Artista e Música duplicados tabelas diferentes;

    0 - SAIR.
    """
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(menu)
        sys.stdout.write("    Opção: ")
        opcao = input()
        if opcao in ["1", 1]:
            return 1
        elif opcao in ["2", 2]:
            return 2
        elif opcao in ["3", 3]:
            return 3
        elif opcao in ["4", 4]:
            return 4
        elif opcao in ["0", 0]:
            break
        else:
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
                pickleMp3 = pickle.dumps(dadosMp3)
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
                if duplicado(dbcursor, tbComputador, dadosMp3.localMp3, "arquivo", seJaExistente=True):
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
                        sql = str('UPDATE "' + tbComputador + '" SET arquivo = ?, basename = ?, fingerprint = ?, ' +
                                  'tamanho = ?, dataAnalise = ?, artista = ?, musica = ?, objeto = ?,'+
                                  'dataModificado = ? ' +
                                  'WHERE "arquivo" = "' + dadosMp3.localMp3 + '"')
                if not sql:
                    sql = str('insert into "' + tbComputador + '"(arquivo, basename, fingerprint, ' +
                              "tamanho, dataAnalise, artista, musica, dataModificado)" +
                              " values (?, ?, ?, ?, ?, ?, ?, ?)")

                sqlValues = [dadosMp3.localMp3, dadosMp3.basename, dadosMp3.fingerprint,
                             dadosMp3.bytes, dadosMp3.dataAnalise, dadosMp3.artista,
                             dadosMp3.titulo, dadosMp3.dataModificado]

                dbcursor.execute(sql, sqlValues)

                if loopCommit >= 50 or i >= qntMp3s:
                    conexaodb.commit()
                    loopCommit = 0
            except Exception as e:
                print("Erro ao gravar informações em banco de", dadosMp3.localMp3, "//", e)
                erroNum += 1
                if erroNum >= 5:
                    print("ERRO(2): Muitos erros(", erroNum, ") durante análise. Processo abortado.")
                    raise RuntimeError
        print("")


def main(banco=sqlite3.connect("dados.db")):
    dbcursor = banco.cursor()
    tbComputador = str(os.uname().nodename + "_v1.0")

    sql = str('CREATE TABLE if not exists "' + tbComputador +
              '"(arquivo TEXT, basename TEXT, fingerprint TEXT, tamanho INT,' +
              'dataAnalise DATE, dataModificado DATE, artista TEXT, musica TEXT)')

    dbcursor.execute(sql)
    conexaodb.commit()

    if len(sys.argv) >= 2:
        localVarrer = os.path.abspath(sys.argv[-1])
        qstVarrerDir = True
        qstCompararPCs = False
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        localVarrer = ""
        qstVarrerDir = questionar("Realizar varredura de \
diretorio?")
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
        #conexaodb.close()


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

    dbcursor = conexaodb.cursor()
    sql = """select * from "conab-dyego_v1.0" where rowid = 5"""
    resultado = dbcursor.execute(sql)
    print(type(resultado), resultado)
    print (dir(dbcursor.execute(sql)))

    teste = DadosMp3(resultado)
    print(teste.artista)
    conexaodb.close()