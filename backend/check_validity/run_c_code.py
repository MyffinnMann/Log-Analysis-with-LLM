import subprocess

def check_log(exe_path, logfile, search_term):

    try:
        result =subprocess.run(
            [exe_path, logfile, search_term], 
            capture_output = True,
            text= True
        )
        #Visa dess output i terminalen (Inget viktigt)
        print(result.stdout)
        print(result.stderr)#std för errror 

        #Statuskod;
        return result.returncode
    except FileNotFoundError:
        print("Error: Kunde inte hitta denna filen/path:", exe_path)
        return -1
    except Exception as e:
        print("Konstigt skit hände:", e)
        return -1
    
#Nedan är enbart ett test:

if __name__ == "__main__":


    executable = "./check_log.cpp" # BYTA UT DENNA TILL DEN RIKTIGA
    logfile = "test.log" #namenet på logfilen (Kan göra det dynamiskt senare)
    search_term = "ERROR" #Det som man kontrollerar/söker efter i loggen, görs dynamiskt senare också. Vet inget annat sätt nu

    check_file_status = check_log(executable, logfile, search_term)
    if check_file_status == 0:
        print("DEN HITTADE YEEEEEEEEEE!!") #Ändra dessa senare....
    else:
        print("FKKKKKK") #Ändra dessa senare....

"""C++ filen måste vara kompilerad och länkad så man enbart kan köra den. Den kompilerade filen måste fiunnas i samma "katalog" annars måste man skriva hela sökvägen"""