#Aqui definiremos el menu principal
def menu():
    print("**************************************************")
    print("**************************************************")
    print("***************** STAR WAR ***********************")
    print("**************** METROPEDIA **********************")
    print("**************************************************")
    print("**************************************************")
    print("Bienvenido a este maravilloso mundo donde veremos si la fuerza esta dentro de ti")
    print("En nuestra metropedia podrás realizar las siguientes acciones:")
    print("1. Lista de peliculas de la saga")
    print("2. Lista de las especies de seres vivos de la saga")
    print("3. Lista de planetas")
    print("4. Grafico de cantidad de personajes nacidos en cada planeta")
    print("5. Graficos de caracteristicas de naves")
    print("6. Estadisticas sobre naves")
    print("7. Construir mision")
    print("8. Visualizar mision")
    print("9. Guardar misiones")
    print("10. Cargar misiones")
    opcion=input("Escoga el número de la opcion correcta\n")
    
    #funcion que verifica la respuesta del usuario, si no es una opcion valida lo devuelve al menu
    if isinstance(opcion, int) and 1 <= opcion <= 10:
        if opcion== "1":
            return True
        elif opcion=="2":
            return True
        elif opcion=="3":
            return True
        elif opcion=="4":
            return True
        elif opcion=="5":
            return True
        elif opcion=="6":
            return True
        elif opcion=="7":
            return True
        elif opcion=="8":
            return True
        elif opcion=="9":
            return True
    else:
        print("Debe seleccionar un numero del 1 al 10, vuelva a intentar")
        menu()
    
    
menu()
