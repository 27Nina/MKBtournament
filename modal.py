import discord
from discord.ext import commands
import re
import pickle
import os
import random
import string
import tempfile


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
is_open = False  # 登録が開いているかどうか

last_registration_number = 0

# 大会名をグローバル変数として定義
tournament_name = None

# 既存のコードの上にこれを追加
current_round = 0  # ラウンド状況を保存する変数

current_round = 0  # 現在のラウンド（0回戦からスタート）
passing_players = {}  # 各ラウンドの通過者を保存
top_n = None  # 通過人数（指定がないとNone）




# ボットの状態（ラウンド、大会名、開かれているかどうか）を保存する関数
def save_bot_state(tournament_format, tournament_name, is_open, current_round):
    with open('bot_state.pkl', 'wb') as f:
        pickle.dump({'tournament_format': tournament_format, 'tournament_name': tournament_name, 'is_open': is_open, 'current_round': current_round}, f)

# ボットの状態をロードする関数
def load_bot_state():
    try:
        with open('bot_state.pkl', 'rb') as f:
            data = pickle.load(f)
            return data.get('tournament_format', None), data.get('tournament_name', None), data.get('is_open', False), data.get('current_round', 0)
    except FileNotFoundError:
        return None, None, False, 0  # デフォルト値









def load_data():
    try:
        with open("data.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        save_data({})  # 新規ファイルを作成
        return {}

def save_data(data):
    with open("data.pkl", "wb") as f:
        pickle.dump(data, f)

# 既存の関数を修正
def save_tournament_state(tournament_format, tournament_name, is_open):
    with open('tournament_state.pkl', 'wb') as f:
        pickle.dump({'tournament_format': tournament_format, 'tournament_name': tournament_name, 'is_open': is_open}, f)

def load_tournament_state():
    try:
        with open('tournament_state.pkl', 'rb') as f:
            data = pickle.load(f)
            tournament_format = data.get('tournament_format', None)
            tournament_name = data.get('tournament_name', None)
            is_open = data.get('is_open', False)  # デフォルト値はFalse
            return tournament_format, tournament_name, is_open
    except FileNotFoundError:
        return None, None, False  # デフォルト値


# on_readyイベントで状態を復元（こちらも修正が必要です）
@bot.event
async def on_ready():
    global is_open, current_round  # グローバル変数を使う宣言
    print("Bot is ready")
    _, _, is_open, current_round = load_bot_state()  # 状態を復元
    await update_status_message()  # ステータスメッセージを更新

# ステータスメッセージを更新する関数
async def update_status_message():
    status_message = f"{current_round}回戦進行中" if current_round > 0 else "1回戦開始前"
    await bot.change_presence(activity=discord.Game(name=status_message))






@bot.command()
@commands.has_permissions(administrator=True)
async def sample(ctx, num: int):
    if num <= 0:
        await ctx.send("人数は1以上で指定してください。")
        return

    sample_data = {}
    for _ in range(num):
        discord_id = ''.join(random.choices(string.digits, k=18))
        registration_number = len(sample_data) + 1
        name = ''.join(random.choices(string.ascii_letters, k=random.randint(1, 10)))

        # ランダムに進行役として設定
        if random.choice([True, False]):
            name += "★進"

        friend_code = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        sample_data[discord_id] = {
            'registration_number': registration_number,
            'name': name,
            'friend_code': friend_code
        }

    # 既存のデータにマージ
    existing_data = load_data()
    existing_data.update(sample_data)

    # データを保存
    save_data(existing_data)
    await ctx.send(f"{num}人分のサンプルデータを作成しました。")

@bot.command()
@commands.has_permissions(administrator=True)
async def next_round(ctx, num_passing: int):
    global current_round, top_n
    top_n = num_passing  # 通過人数を更新
    if current_round < 8:
        current_round += 1
        await ctx.send(f"{current_round}回戦に進行します。次回戦の通過人数は{num_passing}人です。")
        await update_status_message()
    else:
        await ctx.send("これ以上ラウンドを進められません。")





# デバッグ用
@bot.command()
async def datapkl(ctx):
    try:
        with open('data.pkl', 'rb') as f:
            data = pickle.load(f)
        
        # データを一時的な.txtファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
            temp.write(str(data).encode('utf-8'))
            temp_path = temp.name

        # .txtファイルを送信
        await ctx.send(f"data.pklファイルを表示します", file=discord.File(temp_path, 'data.txt'))

        # 一時ファイルを削除
        os.remove(temp_path)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# デバッグ用
@bot.command()
async def rpkl(ctx):
    try:
        with open('result.pkl', 'rb') as f:
            data = pickle.load(f)
        
        # データを一時的な.txtファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
            temp.write(str(data).encode('utf-8'))
            temp_path = temp.name

        # .txtファイルを送信
        await ctx.send(f"result.pklファイルを表示します", file=discord.File(temp_path, 'result.txt'))

        # 一時ファイルを削除
        os.remove(temp_path)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# デバッグ用
@bot.command()
async def gdatapkl(ctx):
    try:
        with open('group_data.pkl', 'rb') as f:
            data = pickle.load(f)
        
        # データを一時的な.txtファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
            temp.write(str(data).encode('utf-8'))
            temp_path = temp.name

        # .txtファイルを送信
        await ctx.send(f"data.pklファイルを表示します", file=discord.File(temp_path, 'data.txt'))

        # 一時ファイルを削除
        os.remove(temp_path)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# デバッグ用
@bot.command()
async def tournamentpkl(ctx):
    try:
        with open('tournament_state.pkl', 'rb') as f:
            data = pickle.load(f)

        # データを一時的な.txtファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
            temp.write(str(data).encode('utf-8'))
            temp_path = temp.name

        # .txtファイルを送信
        await ctx.send(f"tournament_state.pklファイルを表示します", file=discord.File(temp_path, 'tournament_state.txt'))

        # 一時ファイルを削除
        os.remove(temp_path)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

        
#デバッグ用
@bot.command()
@commands.has_permissions(administrator=True)
async def clear_data(ctx):
    try:
        save_data({})
        await ctx.send("登録内容と .pkl ファイルの中身を削除しました。")
    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")



@bot.command()
async def clear_results(ctx):
    if os.path.exists('result.pkl'):
        os.remove('result.pkl')
        await ctx.send("result.pkl ファイルのデータが消去されました。")
    else:
        await ctx.send("result.pkl ファイルが存在しません。")





import os  # osモジュールをインポート

@bot.command()
@commands.has_permissions(administrator=True)
async def tournament(ctx, tournament_format: int, tournament_name: str):
    if tournament_format not in [1, 2, 3, 4]:
        await ctx.send("無効な形式です。1（個人杯）、2（タッグ杯）、3（トリプルス杯）、4（フォーマンセル杯）のいずれかを選んでください。")
        return

    prev_tournament_format, prev_tournament_name, _ = load_tournament_state()

    if prev_tournament_format is not None:
        msg = await ctx.send(f"前回の大会の設定（形式：{prev_tournament_format}、名前：{prev_tournament_name}）が残っています。消去して新しい大会として設定してよろしいでしょうか？")
        
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == "❌":
            await ctx.send("大会の設定をキャンセルしました。")
            return

    # 以前の大会データをリセット
    reset_all_tournament_data()

    # 新しい大会データを保存
    save_tournament_state(tournament_format, tournament_name, True)

    await ctx.send(f"{tournament_name}（形式：{tournament_format}）の設定が完了しました。")



    



    
@bot.command()
@commands.has_permissions(administrator=True)
async def start(ctx):
    global is_open  # 受付状態をグローバル変数で管理
    is_open = True
    await bot.change_presence(activity=discord.Game(name="受付中"))
    await ctx.send("受付を開始しました。")



        

@bot.command()
@commands.has_permissions(administrator=True)
async def end(ctx, num_passing: int):
    global is_open, top_n, current_round  # グローバル変数
    is_open = False
    top_n = num_passing  # 1回戦の通過人数を設定
    current_round = 1  # 1回戦に設定
    await bot.change_presence(activity=discord.Game(name="受付終了"))
    await ctx.send(f"受付を終了しました。1回戦の通過人数は {num_passing} 人です。")


@bot.command()
@commands.has_permissions(administrator=True)
async def register(ctx):
    view = discord.ui.View()
    button1 = discord.ui.Button(label="通常登録", custom_id="normal_register")
    button2 = discord.ui.Button(label="進行役登録", custom_id="shinkou_register")
    
    view.add_item(button1)
    view.add_item(button2)
    
    await ctx.send("大会の登録はこちら", view=view)


@bot.command()
@commands.has_permissions(administrator=True)
async def edit(ctx):
    view = discord.ui.View()
    button3 = discord.ui.Button(label="辞退", custom_id="withdraw")
    button4 = discord.ui.Button(label="登録内容変更", custom_id="change")
    button5 = discord.ui.Button(label="進行役切り替え", custom_id="toggle_shinkou")  # ここを修正
    view.add_item(button3)
    view.add_item(button4)
    view.add_item(button5)
    await ctx.send("登録の変更はこちら", view=view)


@bot.event
async def on_interaction(interaction):
    try:
        global is_open, last_registration_number
        if not is_open:
            await interaction.response.send_message("現在、登録は締め切られています。", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        data = load_data()
        log_channel = bot.get_channel(1146894173908258888)
        await log_channel.send(f"on_interactionが呼び出されました: {interaction.data}")  # ログ出力


        if interaction.data["custom_id"] == "normal_register" or interaction.data["custom_id"] == "shinkou_register":
            if user_id in data:
                await interaction.response.send_message("既に登録されています。", ephemeral=True)
                return
            else:
                last_registration_number += 1  # 登録番号を1増やす
                data[user_id] = {"registration_number": last_registration_number, "name": "", "friend_code": ""}
                save_data(data)

                if interaction.data["custom_id"] == "normal_register":
                    await interaction.response.send_modal(RegistrationModal(user_id, "normal"))
                else:
                    await interaction.response.send_modal(RegistrationModal(user_id, "shinkou"))



        elif interaction.data["custom_id"] == "withdraw":
            if user_id in data:
                del data[user_id]
                save_data(data)
                await interaction.response.send_message("登録を辞退しました。", ephemeral=True)

                # ニックネームを初期化
                guild = interaction.guild
                member = guild.get_member(interaction.user.id)
                await member.edit(nick=None)

                # 大会名のロールを剥奪
                if tournament_name:  # 大会名が定義されている場合のみ
                    role = discord.utils.get(guild.roles, name=tournament_name)
                    if role:  # ロールが存在する場合
                        await member.remove_roles(role)
                
            else:
                await interaction.response.send_message("まだ登録していません。", ephemeral=True)

        elif interaction.data["custom_id"] == "change":
            if user_id in data:
                await interaction.response.send_modal(RegistrationModal(user_id, "change"))
            else:
                await interaction.response.send_message("まだ登録していません。", ephemeral=True)

        elif interaction.data["custom_id"] == "toggle_shinkou":
            await log_channel.send(f"toggle_shinkouが呼び出されました。user_id: {user_id}")  # ログ出力
            if user_id in data:
                await log_channel.send(f"user_id {user_id} はデータに存在します。")  # ログ出力
                if "★進" in data[user_id]["name"]:
                    data[user_id]["name"] = data[user_id]["name"].replace("★進", "")
                    await interaction.response.send_message("進行役を解除しました。", ephemeral=True)
                    await log_channel.send(f"{interaction.user.mention}が{data[user_id]['name']},{data[user_id]['friend_code']}で進行役を解除しました。")
                else:
                    data[user_id]["name"] += "★進"
                    await interaction.response.send_message("進行役に設定しました。", ephemeral=True)
                    await log_channel.send(f"{interaction.user.mention}が{data[user_id]['name']},{data[user_id]['friend_code']}で進行役を設定しました。")
                
                save_data(data)
            else:
                await log_channel.send(f"user_id {user_id} はデータに存在しません。")  # ログ出力
                await interaction.response.send_message("まずは登録してください。", ephemeral=True)

    except Exception as e:
        await log_channel.send(f"エラーが発生しました: {e}")  # エラーログ




class RegistrationModal(discord.ui.Modal):
    def __init__(self, user_id, register_type):
        super().__init__(title="大会登録")
        self.user_id = user_id
        self.register_type = register_type

        self.name_input = discord.ui.TextInput(label="登録名を入力してください", placeholder="登録名", min_length=1, max_length=10)
        self.friend_code_input = discord.ui.TextInput(label="フレコを入力してください", placeholder="xxxx-xxxx-xxxx", min_length=14, max_length=14)
        
        self.add_item(self.name_input)
        self.add_item(self.friend_code_input)

    async def on_submit(self, interaction):
        global last_registration_number
        data = load_data()
        registration_name = self.name_input.value
        friend_code = self.friend_code_input.value

        response_message = ""

        if not re.search(r'[\u4e00-\u9fff]', registration_name):
            if re.fullmatch(r"\d{4}-\d{4}-\d{4}", friend_code):
                last_registration_number += 1
                data[self.user_id] = {
                    "registration_number": last_registration_number,
                    "name": registration_name,
                    "friend_code": friend_code
                }
                save_data(data)

                if self.register_type == "shinkou":
                    registration_name += "★進"
                    log_channel = bot.get_channel(1146894173908258888)
                    await log_channel.send(f"{interaction.user.mention}が{registration_name},{friend_code}で進行役登録をしました。")

                response_message = f"あなたは{registration_name}（フレコ：{friend_code}）で登録が完了しました"

                guild = interaction.guild
                member = guild.get_member(interaction.user.id)
                if self.register_type == "shinkou":
                    await member.edit(nick=registration_name.replace("★進", ""))
                else:
                    await member.edit(nick=registration_name)

                if tournament_name:
                    role = discord.utils.get(guild.roles, name=tournament_name)
                    if role is None:
                        role = await guild.create_role(name=tournament_name)
                    await member.add_roles(role)

                if self.register_type == "change":
                    if self.user_id in data:
                        data[self.user_id]['name'] = registration_name
                        save_data(data)
                        response_message = f"あなたの登録名を{registration_name}に変更しました。"
                        await member.edit(nick=registration_name)

            else:
                response_message = "フレコの形式が不正です。xxxx-xxxx-xxxxの形で入力してください。"
        else:
            response_message = "登録名に漢字は使用できません。"

        await interaction.response.send_message(response_message, ephemeral=True)






# 運営専用: 全ての参加者情報を出力
@bot.command()
@commands.has_permissions(administrator=True)
async def check_all(ctx):
    data = load_data()
    if not data:
        await ctx.send("まだ誰も登録されていません。")
        return

    output = "全ての参加者情報:\n"
    for user_id, user_data in data.items():
        name = user_data['name']
        friend_code = user_data['friend_code']
        registration_number = user_data['registration_number']
        user_info = f"登録名: {name}, フレコ: {friend_code}, 登録番号: {registration_number}\n"

        # Discordのメッセージは2000文字を超えることができないため、途中で送信
        if len(output) + len(user_info) > 1900:  # 余裕を持たせるために1900文字としています
            await ctx.send(f"```\n{output}```")
            output = ""

        output += user_info

    if output:
        await ctx.send(f"```\n{output}```")


        



            
@bot.command(name='check')
async def check_registration(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id in data:
        name = data[user_id]['name']
        friend_code = data[user_id]['friend_code']
        registration_number = data[user_id]['registration_number']  # この行を追加
        await ctx.send(f"```\n登録名: {name}\nフレコ: {friend_code}\n登録番号:{registration_number}```")
                                                                        
    else:
        await ctx.send(f"{ctx.author.mention}, まだ登録されていません。")



make_command_executed = False  # makeコマンドが実行されたかどうかをトラッキング

@bot.command()
async def make(ctx):
    global make_command_executed, current_round

    if make_command_executed:
        msg = await ctx.send("組分けは既に行われました。再度実行してよろしいですか？")
        await msg.add_reaction("✅")  # Yes
        await msg.add_reaction("❌")  # No

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == "❌":
            await ctx.send("組分けの作成をキャンセルしました。")
            return

    confirm_msg = await ctx.send(f"{current_round}回戦の組分けを行います。よろしいですか？")
    await confirm_msg.add_reaction("✅")  # Yes
    await confirm_msg.add_reaction("❌")  # No

    def confirm_check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=confirm_check)

    if str(reaction.emoji) == "❌":
        await ctx.send("組分けの作成をキャンセルしました。")
        return

    # 以降、実際の組分け処理
    # 以降、実際の組分け処理
    if current_round == 0:  # 1回戦開始前の場合
        try:
            with open('data.pkl', 'rb') as file:
                data = pickle.load(file)
        except FileNotFoundError:
            await ctx.send("参加者情報が見つかりません。")
            return

        participants = [v for k, v in data.items()]

    else:  # 1回戦以降の場合
        participants = passing_players.get(current_round - 1, [])
        if not participants:
            await ctx.send("前回戦の通過者データがありません。")
            return
    
    # 以下は元々のコードと同じロジックですが、participantsを使用。
    advance_players = [player for player in participants if "★進" in player['name']]
    other_players = [player for player in participants if "★進" not in player['name']]

    random.shuffle(other_players)

    # ... (以下は変更なし)


    random.shuffle(other_players)

    group_size = 12  # 1組の人数
    num_groups = len(participants) // group_size  # 必要な組の数

    if len(participants) % group_size != 0:
        num_groups += 1  # 余りがある場合、もう一つのグループが必要

    await ctx.send(f"現在の参加者数: {len(participants)}\n必要な組数: {num_groups}")

    if len(participants) < num_groups * group_size:
        await ctx.send("参加者が足りません。")
        return

    groups = []

    for i in range(num_groups):
        group = []

        if advance_players:
            group.append(advance_players.pop(0))

        remaining_slots = group_size - len(group)
        group.extend(other_players[:remaining_slots])
        del other_players[:remaining_slots]

        # 進行役以外の「★進」参加者を一般参加者として追加
        if len(group) < group_size and advance_players:
            extra_needed = group_size - len(group)
            group.extend(advance_players[:extra_needed])
            del advance_players[:extra_needed]

        groups.append(group)

    with open('group_data.pkl', 'wb') as file:
        pickle.dump(groups, file)

    initial_scores = {}
    for i, group in enumerate(groups):
        initial_scores[i+1] = {'names': [player['name'] for player in group], 'scores': [0]*len(group)}
    
    # 初期スコアデータを保存
    with open('result.pkl', 'wb') as f:
        pickle.dump(initial_scores, f)
    
    await ctx.send("組分けと初期スコアデータが作成されました。")
    # ...

    make_command_executed = True  # コマンドが成功した場合にTrueに設定




@bot.command()
async def show(ctx):
    try:
        with open('group_data.pkl', 'rb') as file:
            groups = pickle.load(file)

        output = "組分け結果:\n\n"
        for i, group in enumerate(groups):
            output += f"{i+1}組\n"
            for player in group:
                output += f"{player['name']} ({player['friend_code']})\n"
            if i < len(groups) - 1:
                output += "-\n"

        await ctx.send(output)

    except FileNotFoundError:
        await ctx.send("組分け結果が見つかりません。まずは組分けを実行してください。")



@bot.command()
async def table(ctx, group_number: int):
    try:
        with open('group_data.pkl', 'rb') as file:
            groups = pickle.load(file)
    except FileNotFoundError:
        await ctx.send("組分け結果が見つかりません。まずは組分けを実行してください。")
        return

    if group_number > len(groups) or group_number < 1:
        await ctx.send("指定された組番号は無効です。")
        return

    output = f"!submit {group_number}\n"
    for player in groups[group_number - 1]:
        output += f"{player['name']} 0\n"
    output += "\n"

    await ctx.send(output)



from operator import itemgetter
import pickle

from PIL import Image, ImageDraw, ImageFont


from collections import OrderedDict
import pickle


import urllib.parse




@bot.command()
async def submit(ctx, roomid:int, *, data):
    global current_round  # 現在のラウンド番号を使用

    # 最初の行（この場合は '1'）を除外
    data = '\n'.join(data.split('\n')[1:])
    names, scores = parse_data(data)  # この関数は、テキストデータを解析して名前とスコアのリストを返すものとします。

    # Lorenziのサイトでテーブルを作成するためのURLを生成
    base_url_lorenzi = "https://gb.hlorenzi.com/table.png?data="
    url_table_text = urllib.parse.quote(data)
    image_url = base_url_lorenzi + url_table_text

    # 画像を取得してDiscordに投稿
    embed = discord.Embed(title="スコアボード")
    embed.set_image(url=image_url)
    message = await ctx.send(embed=embed)

    # ユーザーに確認
    await message.add_reaction('☑️')
    await message.add_reaction('❌')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['☑️', '❌']

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except:
        await ctx.send('タイムアウトしました。')
        return

    if str(reaction.emoji) == '☑️':
        try:
            with open('result.pkl', 'rb') as f:
                results = pickle.load(f)
        except FileNotFoundError:
            results = {}

        # 上書きの場合、一度削除して再追加
        if roomid in results:
            del results[roomid]
        results[roomid] = {'names': names, 'scores': scores, 'round': current_round}

        with open('result.pkl', 'wb') as f:
            pickle.dump(results, f)

        await ctx.send('テーブルを保存しました。')
    else:
        await ctx.send('テーブルの保存をキャンセルしました。')


    # ...（以前のコードと同じ）


@bot.command()
async def show_results(ctx):
    try:
        with open('result.pkl', 'rb') as f:
            results = pickle.load(f)
    except FileNotFoundError:
        await ctx.send("結果データが見つかりません。")
        return

    output = "結果一覧:\n\n"
    for roomid, data in results.items():
        output += f"Room ID: {roomid}\n"
        combined = list(zip(data['names'], data['scores']))
        sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)
        for name, score in sorted_combined:
            output += f"{name}: {score}\n"
        output += "-" * 20 + "\n"

    await ctx.send(output)

# データ解析関数
def parse_data(data):
    lines = data.split('\n')
    names = []
    scores = []
    for line in lines:
        if not line.strip():
            continue
        try:
            name, score = line.rsplit(' ', 1)
        except ValueError:
            print(f"Invalid line format: {line}")
            continue
        names.append(name.strip())
        scores.append(int(score.strip()))
    return names, scores















        




bot.run(token)
