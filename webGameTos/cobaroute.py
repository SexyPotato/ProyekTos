from flask import Flask, session, render_template, request, redirect, url_for
from random import randint
import sqlite3 as sql
app = Flask(__name__)
app.secret_key = "moonknight"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<out>')
def user(out):
    return render_template('user.html', out=out)

@app.route('/result',methods=['POST'])
def result():
        if request.method == 'POST':
            class Character:
                def __init__(self):
                    self.name = ""
                    self.health = 1
                    self.health_max = 1
                    self.out = ""#yg dikeluarkan di table pada html
                def do_damage(self, enemy):
                    damage = min(max(randint(0, self.health) - randint(0, enemy.health), 0),enemy.health)
                    enemy.health = enemy.health - damage
                    if damage == 0:
                        self.out = "%s evades %s's attack." % (enemy.name, self.name)
                    else:
                        self.out = "%s hurts %s!" % (self.name, enemy.name)
                    enemy.health <= 0
                    return redirect(url_for('user', out = self.out))
            class Enemy(Character):
                def __init__(self, player):
                    Character.__init__(self)
                    self.name = 'a goblin'
                    self.health = randint(1, player.health)
            class Player(Character):
                def __init__(self):
                    Character.__init__(self)
                    
                    self.state = 'normal'
                    self.health = 10
                    self.health_max = 10
                def explore(self):
                    if self.state != 'normal':
                        self.out =  "%s is too busy right now!" % self.name
                        redirect(url_for('user', out = self.out))
                        #self.enemy_attacks()
                    else:
                        self.out =  "%s explores a twisty passage." % self.name
                    if randint(0, 1):
                        self.enemy = Enemy(self)
                        self.out =  "%s encounters %s!" % (self.name, self.enemy.name)
                        self.state = 'fight'
                    else:
                        if randint(0, 1): self.tired()
                    return redirect(url_for('user', out = self.out))
                def quit(self):
                    self.out =  "%s can't find the way back home, and dies of starvation.\nR.I.P." % self.name
                    self.health = 0
                    return redirect(url_for('user', out = self.out))
                def status(self):
                    self.out =  "%s's health: %d/%d" % (self.name, self.health, self.health_max)
                    return redirect(url_for('user', out = self.out))
                def tired(self):
                    self.out = "%s feels tired." % self.name
                    self.health = max(1, self.health - 1)
                    return redirect(url_for('user', out = self.out))
                def rest(self):
                    if self.state != 'normal':
                        self.out =  "%s can't rest now!" % self.name; self.enemy_attacks()
                    else:
                        self.out =  "%s rests." % self.name
                        if randint(0, 1):
                            self.enemy = Enemy(self)
                            self.out = "%s is rudely awakened by %s!" % (self.name, self.enemy.name)
                            self.state = 'fight'
                            self.enemy_attacks()
                        else:
                            if self.health < self.health_max:
                                self.health = self.health + 1
                            else:
                                self.out =  "%s slept too much." % self.name; self.health = self.health - 1
                    return redirect(url_for('user', out = self.out))
                def flee(self):
                    if self.state != 'fight':
                        self.out = "%s runs in circles for a while." % self.name; self.tired()
                    else:
                        if randint(1, self.health + 5) > randint(1, self.enemy.health):
                            self.out =  "%s flees from %s." % (self.name, self.enemy.name)
                            self.enemy = None
                            self.state = 'normal'
                        else:
                            self.out =  "%s couldn't escape from %s!" % (self.name, self.enemy.name); self.enemy_attacks()
                            return redirect(url_for('user', out = self.out))
                '''def enemy_attacks(self):
                    if self.enemy.do_damage(self):
                        self.out = "%s was slaughtered by %s!!!\nR.I.P." %(self.name, self.enemy.name)
                        return redirect(url_for('user', out = self.out))'''
                def attack(self):
                    if self.state != 'fight':
                        self.out =  "%s swats the air, without notable results." % self.name; self.tired()
                    else:
                        if self.do_damage(self.enemy):
                            self.out =  "%s executes %s!" % (self.name, self.enemy.name)
                            self.enemy = None
                            self.state = 'normal'
                            if randint(0, self.health) < 10:
                                self.health = self.health + 1
                                self.health_max = self.health_max + 1
                                self.out =  "%s feels stronger!" % self.name
                            else: self.enemy_attacks()
                    return redirect(url_for('user', out = self.out))
            Commands = {
                'quit': Player.quit,
                'status': Player.status,
                'rest': Player.rest,
                'explore': Player.explore,
                'flee': Player.flee,
                'attack': Player.attack,
            }
            p = Player()
            p.name = session['user']
            p.out = "%s explores a twisty passage." % (session['user'])
            while(p.health > 0):
                line = request.form['answer']
                if len(line) > 0:
                    commandFound = False
                    for c in Commands.keys():
                        if line[0] == c[0]:
                            Commands[c](p)
                            redirect(url_for('user', out = p.out))
                            commandFound = True
                            break
                    if not commandFound:
                        p.out =  "%s doesn't understand the suggestion." % p.name
            return redirect(url_for('user', out = p.out))

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/signup')
def signup():
   return render_template('signup.html')

@app.route('/login_user', methods=['POST'])
def login_user():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['pass']
		with sql.connect("database.db") as data:
			inp = data.cursor()
			inp.execute("SELECT COUNT(*) FROM users WHERE username = ? AND password = ?" ,(username, password))
			rows = inp.fetchall();
			data.commit()
		for i in rows:
			if i[0] >= 1:
				session['user'] = username
				return redirect(url_for('user', out=session['user']))
			else:
				return redirect(url_for('signup'))
		data.close

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == "POST":
        try:
            username = request.form['username']
            password = request.form['pass']
            with sql.connect("database.db") as file:
                inp = file.cursor()
                inp.execute("INSERT INTO users (username, password) VALUES (?, ?)",(username, password))
                file.commit()
                print "Data success!"
        except: 
            file.rollback()
        finally:
            file.close()
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
   session.pop('user', None)
   return redirect(url_for('index'))

if __name__ == '__main__':
   app.run('0.0.0.0', port=5061, debug=True)
