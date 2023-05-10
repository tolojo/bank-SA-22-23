import sys,re

ip_regex = '''(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)
            (\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}'''

num_regex = "^[-+]?[0-9]+$"

float_regex = "^[0-9]*\.[0-9]{2}$"

name_regex = "^[_\\-\\.0-9a-z]+$"

forb_names = [".",".."]

acc_regex = "^[0-9]+$"

class Checker :

    def __init__(self):

        self.store = 0

    def check_mbec_args(self,args) :

        #main variables 
        account = auth_file = dest_ip = dest_port = user_file = vvc_file = None
            
        ARG_LEN = len(args)

        sequential = 1 
        acc_given = mode_given = 0

        #Flag appearances counter dictionaries to keep track duplicates
        param_dict = {"-a" : [0,None] ,"-s" : [0,None],"-i": [0,None] ,
                    "-p": [0,None] ,"-u": [0,None] ,"-v": [0,None] }
        
        modes_dict = {"-n" : [0,None] ,"-d" : [0,None],"-c": [0,None] ,
                    "-g" : [0,None] , "-m" : [0,None]}
        
        #Try and catch/main loop to get all args. 
        try : 
            for i in range(1,ARG_LEN):

                arg = args[i] if len(args[i]) < 4096 else sys.exit()

                if arg[0] != "-" : continue

                if len(arg) > 2 :
                    arg, n_arg = arg[0:2], arg[2:]
                else :
                    try :
                        n_arg = args[i+1]
                    except IndexError:
                        pass

                for flag in param_dict:

                    if arg == flag:
                        param_dict[flag][0] = 1 if param_dict[flag][0] == 0 else sys.exit(130)

                        if arg in ["-a","-p"]: 

                            try :
                                if arg == "-a" and n_arg[0] != "-" and self.check_account(n_arg) :
                                    
                                    param_dict[flag][1] = n_arg 
                                    acc_given = 1
                                
                                if arg == "-p" and self.check_nr(n_arg) and self.check_port(int(n_arg)) :
                                    param_dict[flag][1] = n_arg 

                            except ValueError:
                                sys.exit(130)
                        
                        if arg == "-i": param_dict[flag][1] = n_arg if self.check_ip(n_arg) == 1 else None

                        if arg in ["-s","-u","-v"]: param_dict[flag][1] = n_arg if n_arg[0] != "-" \
                                and self.check_filename(n_arg) else None
                
                for flag in modes_dict:

                    if arg == flag:

                        modes_dict[flag][0] = 1 if modes_dict[flag][0] == 0 else sys.exit(130)

                        if arg in ["-n","-d","-c","-m"]: 

                            try :
                                modes_dict[flag][1] =n_arg if n_arg[0] != "-" and \
                                    self.check_float(n_arg) == 1 else None 
                            except ValueError:
                                sys.exit(130)

                        if arg == "-m": self.store = 1

                        mode_given = 1

                        raise StopIteration

        except StopIteration:
            pass

        account = param_dict["-a"][1] if acc_given == 1 and mode_given == 1 else None
    
        if account == None : account = param_dict["-v"][1].split("_")[0]
                
        sys.exit(130) if account == None else None

        defaults = ["bank.auth","127.0.0.1", 5000 if self.store else 3000 , 
                    str(account) + ".user",str(account) + "_" + str(sequential) + ".card"]

        #removes first element because -a doesnt have default
        tmp_param_dict = dict(list(param_dict.items())[1:])

        #applies defaults
        auth_file,dest_ip,dest_port,user_file,vvc_file = map (lambda v,d: tmp_param_dict[v][1] 
                                                          if tmp_param_dict[v][1] != None 
                                                          else d, tmp_param_dict, defaults)

        return account,auth_file,dest_ip,dest_port,user_file,vvc_file,modes_dict
    
    def check_args(self,args,st) :

        port = auth_file = None
        #Flag appearances counter dictionaries to keep track duplicates
        param_dict = {"-p" : [0,None] ,"-s" : [0,None]}

        ARG_LEN = len(args)

        for i in range(1,ARG_LEN):

            arg = args[i] if len(args[i]) < 4096 else sys.exit()

            if arg[0] != "-" : continue

            if len(arg) > 2 :
                arg, n_arg = arg[0:2], arg[2:]
            else :
                try :
                    n_arg = args[i+1]
                except IndexError:
                    pass

            for flag in param_dict:

                if arg == flag:
                    
                    param_dict[flag][0] = 1 if param_dict[flag][0] == 0 else sys.exit(130)

                    try :

                        if arg == "-p" and self.check_nr(n_arg) and self.check_port(int(n_arg)) :
                            param_dict[flag][1] = n_arg  
        
                        if arg == "-s" : param_dict[flag][1] = n_arg if n_arg[0] != "-" \
                                and self. check_filename(n_arg) else None
                            
                    except ValueError:
                        sys.exit(130)
        

        defaults = [3000 if st == 0 else 5000,"bank.auth"]

        tmp_param_dict = dict(list(param_dict.items()))

        port,auth_file = map (lambda v,d: tmp_param_dict[v][1] 
                                if tmp_param_dict[v][1] != None 
                                else d, tmp_param_dict, defaults)

        return port,auth_file
    
    def is_store_op(self):

        return self.store
    
    def check_account(self,name): return 1 if re.match(r"{}".format(acc_regex), name) else sys.exit(130)
    
    def check_ip(self,ip): return 1 if re.match(r"{}".format(ip_regex), ip) else sys.exit(130)

    def check_nr(self,number): return 1 if re.match(r"{}".format(num_regex), number) else sys.exit(130)
    
    def check_float(self,number): return 1 if re.match(r"{}".format(float_regex), number) else sys.exit(130)

    def check_filename(self,filename): return 1 if re.match(r"{}".format(name_regex), filename) \
            and 1 <= len(filename) <= 127 and filename not in forb_names else sys.exit(130)

    def check_port(self,port): return 1 if 1024 <= port <= 65535 else sys.exit(130)