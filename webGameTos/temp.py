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
                redirect(url_for('user', out = self.out))
                return enemy.health <= 0
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
            def quit(self):
                self.out =  "%s can't find the way back home, and dies of starvation.\nR.I.P." % self.name
                self.health = 0
                redirect(url_for('user', out = self.out))
            def status(self):
                self.out =  "%s's health: %d/%d" % (self.name, self.health, self.health_max)
                redirect(url_for('user', out = self.out))
            def tired(self):
                self.out = "%s feels tired." % self.name
                self.health = max(1, self.health - 1)
                redirect(url_for('user', out = self.out))
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
                redirect(url_for('user', out = self.out))
            def explore(self):
                if self.state != 'normal':
                    self.out =  "%s is too busy right now!" % self.name
                    self.enemy_attacks()
                else:
                    self.out =  "%s explores a twisty passage." % self.name
                    if randint(0, 1):
                        self.enemy = Enemy(self)
                        self.out =  "%s encounters %s!" % (self.name, self.enemy.name)
                        self.state = 'fight'
                    else:
                        if randint(0, 1): self.tired()
                redirect(url_for('user', out = self.out))
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
                        redirect(url_for('user', out = self.out))
            def enemy_attacks(self):
                if self.enemy.do_damage(self):
                    self.out = "%s was slaughtered by %s!!!\nR.I.P." %(self.name, self.enemy.name)
                    redirect(url_for('user', out = self.out))
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
                redirect(url_for('user', out = self.out))
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
            args = line.split()
            if len(args) > 0:
                commandFound = False
                for c in Commands.keys():
                    if args[0] == c[:len(args[0])]:
                        Commands[c](p)
                        commandFound = True
                        break
                if not commandFound:
                    p.out =  "%s doesn't understand the suggestion." % p.name
        return redirect(url_for('user', out = p.out))