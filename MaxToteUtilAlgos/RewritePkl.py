import pickle

def rewrite(filename):
    with open(filename, 'rb') as dict_file3nvp:
        totes = pickle.load(dict_file3nvp)
        result_totes = {}
        for id,tote in enumerate(totes):
            re_tote = {}
            for key,val in enumerate(tote):
                if key == "CONTENTS":
                    pass
                try:
                    key = int(key)
                except:
                    pass

                re_tote[key] = val
