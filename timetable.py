import json, random

dani = {1:'pon', 2:'uto', 3:'sre', 4:'cet', 5:'pet'}

ucionice = []

class Cas():

    def __init__(self, predmet, tip, nastavnik, grupe, uc_id, trajanje, ucionica, termin):
        self.predmet = predmet
        self.tip = tip
        self.nastavnik = nastavnik
        self.grupe = grupe
        self.uc_id = uc_id
        self.trajanje = trajanje
        self.ucionica = ucionica
        self.termin = termin

    def __repr__(self):
        return f'{self.predmet} ({self.tip}), {self.nastavnik}, {self.termin}, {self.ucionica}, {self.grupe}'

class Hromozom():

    def __init__(self, casovi):
        self.raspored = []

        dan = 1
        sat = 9
        s_ucionice = {}
        for gr_u in ucionice:
            for u in ucionice[gr_u]:
                s_ucionice[u] = 0

        nerasporedjeni = 0

        while len(casovi) > 0:
            print(len(casovi))
            cas = casovi.pop(0)
            predmet = cas['Predmet']
            tip = cas['Tip']
            nastavnik = cas['Nastavnik']
            grupe = cas['Grupe']
            gr_u = cas['Ucionica']
            trajanje = int(cas['Trajanje'])
            ucionica = None
            termin = None

            uc_nadjena = False
            for u in ucionice[gr_u]:
                if s_ucionice[u] == 0:
                    s_ucionice[u] = trajanje
                    uc_nadjena = True
                    break

            if (not uc_nadjena):
                nerasporedjeni += 1
                if nerasporedjeni > 5:
                    sat += 1
                    if sat == 20:
                        dan += 1
                        if dan > 5:
                            print('e jeste sad, i subotom na faks')

                    for u in s_ucionice:
                        s_ucionice[u] = 0 if s_ucionice[u] == 0 else s_ucionice[u] - 1

                    nerasporedjeni = 0

                casovi.append(cas)
                continue

            if sat + trajanje > 21:
                casovi.append(cas)
                nerasporedjeni += 1
                continue

            print('TEST')
            nerasporedjeni = 0
            termin = f'{dani[dan]}, {sat}h-{sat + trajanje}'
            self.raspored.append(Cas(predmet, tip, nastavnik, grupe, gr_u, trajanje, ucionica, termin))

    def evaluacija(self):
        pass

    def __repr__(self):
        return '\n'.join(self.raspored)       


class Hromozom2():

    def __init__(self, casovi):
        self.raspored = []
        dan = 1
        sat = 9
        slobodne_uc = []
        for id in ucionice:
            for u in ucionice[id]:
                slobodne_uc.append(u)

        promasaj = 0
        pr_naj_t = 0
                
        while len(casovi) > 0:
            cas = casovi.pop(0)
            predmet = cas['Predmet']
            tip = cas['Tip']
            nastavnik = cas['Nastavnik']
            grupe = cas['Grupe']
            uc_id = cas['Ucionica']
            t = int(cas['Trajanje'])
            pr_naj_t = max(pr_naj_t, t)
            termin = None
            ucionica = None

            uc_nadjena = False
            for u in ucionice[uc_id]:
                if u in slobodne_uc:
                    ucionica = slobodne_uc.pop(slobodne_uc.index(u))
                    uc_nadjena = True

            if not uc_nadjena:
                promasaj += 1
                if promasaj > 5:
                    sat += pr_naj_t
                    pr_naj_t = 0

                casovi.append(cas)
                continue

            if sat + 3 > 21:
                dan += 1
                sat = 9
                if dan > 5:
                    print('Woah, woah, woah! Slow down there, buddy!')

            termin = f'{dani[dan]}, {sat}h-{sat + t}'
            self.raspored.append(Cas(predmet, tip, nastavnik, grupe, uc_id, t, ucionica, termin))
            
    def evaluacija(self):
        pass

    def __repr__(self):
        return '\n'.join(self.raspored)

class Populacija():

    def __init__(self, mi, lm, casovi):
        self.mi = mi
        self.lm = lm
        self.hromozomi = [Hromozom(casovi) for i in range(self.mi + self.lm)]

    def evaluacija(self):
        pass

    def selekcija(self):
        pass

    def mutacija(self):
        pass


if __name__ == '__main__':

    data = None
    with open('ulaz1.json', 'r') as f:
        data = json.load(f)

    ucionice = data['Ucionice']
    casovi = data['Casovi']

    p = Populacija(10, 10, casovi)
    print(p.hromozomi[0])
