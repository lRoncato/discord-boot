import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Carregando variáveis de ambiente
load_dotenv()

# Substituindo pelo token no arquivo .env
TOKEN = os.getenv("TOKEN")

# Verificando se o token foi carregado corretamente
if TOKEN is None:
    raise ValueError("Token não encontrado no arquivo .env. Verifique se o nome da variável está correto.")

# Definindo as intents
intents = discord.Intents.default()
intents.message_content = True  # Permite ler o conteúdo das mensagens
intents.members = True  # Permite ler os membros do servidor

# Nome da organização
ORG = "PF"

# Criando o bot com prefixo de comando "/"
bot = commands.Bot(command_prefix="/", intents=intents)

# Canal específico onde as matrículas serão enviadas
CANAL_MATRICULA = 1349141308383428670  # Substitua pelo ID do canal

# Função para carregar as matrículas
def carregar_matriculas():
    try:
        with open("matriculas.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar as matrículas
def salvar_matriculas(data):
    with open("matriculas.json", "w") as f:
        json.dump(data, f, indent=4)

# Comando para gerar a matrícula
@bot.command()
async def matricula(ctx):
    # Carregando as matrículas existentes
    dados = carregar_matriculas()
    
    # Verificando se o usuário já tem matrícula
    if str(ctx.author.id) in dados:
        await ctx.send(f"{ctx.author.mention}, você já possui uma matrícula!")
        return

    # Gerando a matrícula
    ano = "2025"  # Você pode modificar o ano conforme necessário
    ultimo_numero = dados.get(ano, 0) + 1
    dados[ano] = ultimo_numero
    salvar_matriculas(dados)

    # Formatando a matrícula
    numero_formatado = f"{ultimo_numero:04d}"
    matricula_final = f"{ORG}-{ano}-{numero_formatado}"

    # Salvando a matrícula do usuário
    dados[str(ctx.author.id)] = matricula_final
    salvar_matriculas(dados)

    # Enviando a matrícula para o canal específico
    canal = bot.get_channel(CANAL_MATRICULA)
    if canal:
        await canal.send(f"Nova matrícula gerada para {ctx.author.mention}: {matricula_final}")

    # Enviando a mensagem privada para o usuário
    await ctx.author.send(f"✅ Sua matrícula foi gerada: **{matricula_final}**")
    
    # Apagar a mensagem no canal de onde a solicitação foi feita
    await ctx.message.delete()

# Comando para verificar a matrícula
@bot.command()
async def minha_matricula(ctx):
    dados = carregar_matriculas()
    matricula = dados.get(str(ctx.author.id))
    
    if matricula:
        await ctx.send(f"{ctx.author.mention}, sua matrícula é: **{matricula}**")
    else:
        await ctx.send(f"{ctx.author.mention}, você ainda não possui uma matrícula.")

# Comando para apagar a matrícula (somente para administradores)
@bot.command()
@commands.has_permissions(administrator=True)
async def apagar_matricula(ctx, membro: discord.Member):
    dados = carregar_matriculas()
    
    if str(membro.id) in dados:
        del dados[str(membro.id)]
        salvar_matriculas(dados)
        await ctx.send(f"A matrícula de {membro.mention} foi apagada.")
    else:
        await ctx.send(f"{membro.mention} não possui matrícula registrada.")

# Mensagem de erro caso o usuário não tenha permissões para apagar a matrícula
@apagar_matricula.error
async def apagar_matricula_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, você não tem permissão para apagar matrículas.")

# Rodando o bot
bot.run(TOKEN)
