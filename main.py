import requests
import matplotlib.pyplot as plt
import csv
import statistics

class Conexion:
    #conexion principal a la plataforma swapi
    url_api = "https://www.swapi.tech/api"

    def __init__(self):
        pass
    #dependiendo de la informacion se obtiene el url
    def obtener_datos(self, endpoint):
        url = f"{self.url_api}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('result', {}).get('properties', {})
        else:
            raise Exception(f"No se pudo realizar la conexion {url}: {response.status_code}")

    def obtener_todos_datos(self, endpoint, key='results'):
        url = f"{self.url_api}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get(key, [])
        else:
            raise Exception(f"No se pudo realizar la conexión {url}: {response.status_code}")


class Pelicula:
    def __init__(self, titulo, episodio_id, fecha_lanzamiento, opening_crawl, director):
        self.titulo = titulo
        self.episodio_id = episodio_id
        self.fecha_lanzamiento = fecha_lanzamiento
        self.opening_crawl = opening_crawl
        self.director = director

    @classmethod
    def from_api_data(cls, data):
        return cls(
            titulo=data.get('title'),
            episodio_id=data.get('episode_id'),
            fecha_lanzamiento=data.get('release_date'),
            opening_crawl=data.get('opening_crawl'),
            director=data.get('director')
        )

    @staticmethod
    def list_films(client):
        films_data = client.obtener_todos_datos('films','result')
        films = [Pelicula.from_api_data(film['properties']) for film in films_data]
        return films

    def mostrar_film(self):
        print(f"Titulo: {self.titulo}")
        print(f"Número episodio: {self.episodio_id}")
        print(f"Fecha de lanzamiento: {self.fecha_lanzamiento}")
        print(f"Opening Crawl: {self.opening_crawl}")
        print(f"Director: {self.director}")
        print("-" * 40)
        
        
class Species:
    species_ids = {}  # Diccionario para almacenar IDs de especies y sus nombres

    def __init__(self, name, height, classification, homeworld, language, characters, films):
        self.name = name
        self.height = height
        self.classification = classification
        self.homeworld = homeworld
        self.language = language
        self.characters = characters
        self.films = films

    @classmethod
    def from_api_data(cls, data, client):
        # Obtener el nombre del planeta de origen si existe un homeworld
        homeworld_name = "Desconocido"
        if data.get('homeworld'):
            homeworld_data = client.obtener_datos(data['homeworld'].replace(client.url_api + '/', ''))
            homeworld_name = homeworld_data.get('name', "Desconocido")

        # Obtener los nombres de los personajes a partir de las URLs
        character_names = []
        for char_url in data.get('people', []):
            char_data = client.obtener_datos(char_url.replace(client.url_api + '/', ''))
            character_names.append(char_data.get('name', 'Desconocido'))

        # Obtener los nombres de los episodios a partir de las URLs
        film_titles = []

        return cls(
            name=data.get('name'),
            height=data.get('average_height'),
            classification=data.get('classification'),
            homeworld=homeworld_name,
            language=data.get('language'),
            characters=character_names,
            films=film_titles
        )

    @staticmethod
    def list_species(client):
        species_data = client.obtener_todos_datos('species', 'results')
        species_list = []
        
        # Limpiar el diccionario de IDs de especies
        Species.species_ids.clear()
        
        for species in species_data:
            species_details = client.obtener_datos(f'species/{species["uid"]}')
            species_obj = Species.from_api_data(species_details, client)
            species_list.append(species_obj)
            
            # Guardar el ID de la especie y su nombre
            Species.species_ids[species["uid"]] = species_obj
        
        # Después de crear todas las especies, asociarlas con las películas
        Species.asociar_peliculas(client)
        return species_list
    
    @staticmethod
    def asociar_peliculas(client):
        films_data = client.obtener_todos_datos('films', 'result')
        
        for film in films_data:
            film_details = client.obtener_datos(f'films/{film["uid"]}')
            film_title = film_details['title']
            
            for species_url in film_details['species']:
                species_id = species_url.split('/')[-1]
                if species_id in Species.species_ids:
                    Species.species_ids[species_id].films.append(film_title)
                else:
                    print(f"No se encontró especie con ID {species_id}")
    
    def mostrar_especie(self):
        print(f"Nombre: {self.name}")
        print(f"Altura: {self.height}")
        print(f"Clasificación: {self.classification}")
        print(f"Nombre planeta de origen: {self.homeworld}")
        print(f"Lengua materna: {self.language}")
        print(f"Personajes que pertenecen a la especie: {', '.join(self.characters)}")
        print(f"Episodios en los que aparecen: {', '.join(self.films)}")
        print("-" * 40)

        
class Planet:
    def __init__(self, name, rotation_period, orbital_period, population, climate, films, residents):
        self.name = name
        self.rotation_period = rotation_period
        self.orbital_period = orbital_period
        self.population = population
        self.climate = climate
        self.films = films
        self.residents = residents

    @classmethod
    def from_api_data(cls, data, film_titles_dict, character_names_dict):
        # Obtener los nombres de las películas
        film_titles = [film_titles_dict.get(film_url, "Desconocido") for film_url in data.get('films', [])]

        # Obtener los nombres de los personajes
        resident_names = [character_names_dict.get(resident_url, "Desconocido") for resident_url in data.get('residents', [])]

        return cls(
            name=data.get('name'),
            rotation_period=data.get('rotation_period'),
            orbital_period=data.get('orbital_period'),
            population=data.get('population'),
            climate=data.get('climate'),
            films=film_titles,
            residents=resident_names
        )

    @staticmethod
    def list_planets(client):
        # Cargar todas las películas y personajes en diccionarios para acceso rápido
        films_data = client.obtener_todos_datos('films', 'result')
        characters_data = client.obtener_todos_datos('people', 'results')

        # Verificar si se obtuvieron datos
        print("Datos de películas obtenidos:", films_data)
        print("Datos de personajes obtenidos:", characters_data)

        # Crear diccionarios de títulos de películas y nombres de personajes
        film_titles_dict = {}
        for film in films_data:
            if 'properties' in film:
                film_titles_dict[film['properties']['url']] = film['properties']['title']

        character_names_dict = {}
        for character in characters_data:
            if 'url' in character:
                character_details = client.obtener_datos(f'people/{character["uid"]}')
                if 'result' in character_details and 'properties' in character_details['result']:
                    character_names_dict[character['url']] = character_details['result']['properties']['name']

        # Verificar diccionarios creados
        print("Diccionario de títulos de películas:", film_titles_dict)
        print("Diccionario de nombres de personajes:", character_names_dict)

        # Cargar los datos de los planetas y asociar las películas y personajes
        planets_data = client.obtener_todos_datos('planets', 'results')
        planets_list = []

        # Verificar datos de planetas
        print("Datos de planetas obtenidos:", planets_data)

        for planet in planets_data:
            planet_details = client.obtener_datos(f'planets/{planet["uid"]}')
            if 'result' in planet_details and 'properties' in planet_details['result']:
                planet_obj = Planet.from_api_data(planet_details['result']['properties'], film_titles_dict, character_names_dict)
                planets_list.append(planet_obj)

        # Verificar lista de planetas
        print("Lista de planetas procesados:", planets_list)

        return planets_list

    def mostrar_planeta(self):
        print(f"Nombre: {self.name}")
        print(f"Período de órbita: {self.orbital_period}")
        print(f"Período de rotación: {self.rotation_period}")
        print(f"Cantidad de habitantes: {self.population}")
        print(f"Tipo de clima: {self.climate}")
        print(f"Episodios en los que aparece: {', '.join(self.films) if self.films else 'N/A'}")
        print(f"Personajes originarios: {', '.join(self.residents) if self.residents else 'N/A'}")
        print("-" * 40)

class Character:
    def __init__(self, name, homeworld, gender, species, films, starships, vehicles):
        self.name = name
        self.homeworld = homeworld
        self.gender = gender
        self.species = species
        self.films = films
        self.starships = starships
        self.vehicles = vehicles

    @classmethod
    def from_api_data(cls, data, homeworld_name, species_name, film_titles, starship_names, vehicle_names):
        return cls(
            name=data.get('name'),
            homeworld=homeworld_name,
            gender=data.get('gender'),
            species=species_name,
            films=film_titles,
            starships=starship_names,
            vehicles=vehicle_names
        )

    @staticmethod
    def search_character(client, query):
        characters_data = client.obtener_todos_datos('people', 'results')
        
        matching_characters = []

        for character in characters_data:
            character_details = client.obtener_datos(f'people/{character["uid"]}')

            # Obtener el nombre del planeta de origen
            homeworld_name = "Desconocido"
            if character_details.get('homeworld'):
                homeworld_data = client.obtener_datos(character_details['homeworld'].replace(client.url_api + '/', ''))
                homeworld_name = homeworld_data.get('name', "Desconocido")

            # Obtener el nombre de la especie
            species_name = "Desconocido"
            if character_details.get('species'):
                species_data = client.obtener_datos(character_details['species'][0].replace(client.url_api + '/', ''))
                species_name = species_data.get('name', "Desconocido")

            # Obtener los títulos de las películas
            film_titles = []
            for film_url in character_details.get('films', []):
                film_data = client.obtener_datos(film_url.replace(client.url_api + '/', ''))
                film_titles.append(film_data.get('title', "Desconocido"))

            # Obtener los nombres de las naves espaciales
            starship_names = []
            for starship_url in character_details.get('starships', []):
                starship_data = client.obtener_datos(starship_url.replace(client.url_api + '/', ''))
                starship_names.append(starship_data.get('name', "Desconocido"))

            # Obtener los nombres de los vehículos
            vehicle_names = []
            for vehicle_url in character_details.get('vehicles', []):
                vehicle_data = client.obtener_datos(vehicle_url.replace(client.url_api + '/', ''))
                vehicle_names.append(vehicle_data.get('name', "Desconocido"))

            if query.lower() in character_details.get('name', "").lower():
                character_obj = Character.from_api_data(
                    character_details,
                    homeworld_name,
                    species_name,
                    film_titles,
                    starship_names,
                    vehicle_names
                )
                matching_characters.append(character_obj)

        return matching_characters

    def mostrar_personaje(self):
        print(f"Nombre: {self.name}")
        print(f"Nombre del planeta de origen: {self.homeworld}")
        print(f"Género: {self.gender}")
        print(f"Especie: {self.species}")
        print(f"Títulos de los episodios en los que interviene: {', '.join(self.films) if self.films else 'N/A'}")
        print(f"Nombre de las naves que utiliza: {', '.join(self.starships) if self.starships else 'N/A'}")
        print(f"Nombre de los vehículos que utiliza: {', '.join(self.vehicles) if self.vehicles else 'N/A'}")
        print("-" * 40)

class Starship:
    def __init__(self, name, hyperdrive_rating, mglt, max_atmosphering_speed, cost_in_credits):
        self.name = name
        self.hyperdrive_rating = hyperdrive_rating
        self.mglt = mglt
        self.max_atmosphering_speed = max_atmosphering_speed
        self.cost_in_credits = cost_in_credits

    @classmethod
    def from_api_data(cls, data):
        return cls(
            name=data.get('name'),
            hyperdrive_rating=data.get('hyperdrive_rating', 'N/A'),
            mglt=data.get('MGLT', 'N/A'),
            max_atmosphering_speed=data.get('max_atmosphering_speed', 'N/A'),
            cost_in_credits=data.get('cost_in_credits', 'N/A')
        )

    @staticmethod
    def list_starships(client):
        starships_data = client.obtener_todos_datos('starships', 'results')
        starships_list = []
        for starship in starships_data:
            # Acceder a result['properties'] para obtener los detalles de la nave
            starship_details = client.obtener_datos_individuales(starship['url'])
            starships_list.append(Starship.from_api_data(starship_details['result']['properties']))
        return starships_list
    
##Funciones del menu
#opcion 1
def mostrar_lista_peliculas(client):
    peliculas = Pelicula.list_films(client)
    print("\n*** Lista de Películas de la Saga Star Wars ***\n")
    for pelicula in peliculas:
        pelicula.mostrar_film()
#opcion 2
def mostrar_lista_especies(client):
    especies = Species.list_species(client)
    print("\n*** Lista de Especies de la Saga Star Wars ***\n")
    for especie in especies:
        especie.mostrar_especie()
        
# Opción 3 del menú
def mostrar_lista_planetas(client):
    planetas = Planet.list_planets(client)
    print("\n*** Lista de Planetas de la Saga Star Wars ***\n")
    for planeta in planetas:
        planeta.mostrar_planeta()       
# Opción 4 del menú     
def buscar_personaje(client):
    query = input("Ingrese el nombre o parte del nombre del personaje que desea buscar:\n")
    personajes = Character.search_character(client, query)
    print(client)
    if personajes:
        print(f"\n*** Resultados de la búsqueda para '{query}' ***\n")
        for personaje in personajes:
            personaje.mostrar_personaje()
    else:
        print(f"\nNo se encontraron personajes que coincidan con '{query}'.\n")
        
# Opcion5 del menu()
def obtener_personajes_por_planeta(client):
    # Obtener todos los personajes
    characters_data = client.obtener_todos_datos('people', 'results')
    
    # Crear un diccionario para contar los personajes por planeta
    planet_counts = {}
    
    for character in characters_data:
        character_details = client.obtener_datos(f'people/{character["uid"]}')
        
        # Obtener el nombre del planeta de origen
        homeworld_name = "Desconocido"
        if character_details.get('homeworld'):
            homeworld_data = client.obtener_datos(character_details['homeworld'].replace(client.url_api + '/', ''))
            homeworld_name = homeworld_data.get('name', "Desconocido")
        
        # Contar el planeta en el diccionario
        if homeworld_name in planet_counts:
            planet_counts[homeworld_name] += 1
        else:
            planet_counts[homeworld_name] = 1
    
    return planet_counts

def graficar_personajes_por_planeta(client):
    # Obtener los datos de personajes por planeta
    planet_counts = obtener_personajes_por_planeta(client)
    
    # Ordenar los datos para el gráfico
    planet_names = list(planet_counts.keys())
    counts = list(planet_counts.values())
    
    # Crear el gráfico
    plt.figure(figsize=(12, 8))
    plt.bar(planet_names, counts, color='skyblue')
    plt.xlabel('Planeta')
    plt.ylabel('Número de Personajes')
    plt.title('Cantidad de Personajes Nacidos en Cada Planeta')
    plt.xticks(rotation=90)
    plt.tight_layout()  # Ajusta el diseño para evitar el recorte de etiquetas
    plt.show()

def opcion_5(client):
    print("Generando gráfico de cantidad de personajes nacidos en cada planeta...")
    graficar_personajes_por_planeta(client)       
def exportar_datos_csv(planet_counts, filename='personajes_por_planeta.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Planeta', 'Número de Personajes'])
        for planeta, cantidad in planet_counts.items():
            writer.writerow([planeta, cantidad])
    print(f"Datos exportados a {filename}")

def obtener_personajes_por_planeta(client):
    # Obtener todos los personajes
    characters_data = client.obtener_todos_datos('people', 'results')
    
    # Crear un diccionario para contar los personajes por planeta
    planet_counts = {}
    
    for character in characters_data:
        character_details = client.obtener_datos(f'people/{character["uid"]}')
        
        # Obtener el nombre del planeta de origen
        homeworld_name = "Desconocido"
        if character_details.get('homeworld'):
            homeworld_data = client.obtener_datos(character_details['homeworld'].replace(client.url_api + '/', ''))
            homeworld_name = homeworld_data.get('name', "Desconocido")
        
        # Contar el planeta en el diccionario
        if homeworld_name in planet_counts:
            planet_counts[homeworld_name] += 1
        else:
            planet_counts[homeworld_name] = 1
    
    # Exportar los datos a CSV
    exportar_datos_csv(planet_counts)
    
    return planet_counts  

def leer_datos_csv(filename='personajes_por_planeta.csv'):
    planet_counts = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            planet_counts[row['Planeta']] = int(row['Número de Personajes'])
    return planet_counts

def graficar_personajes_por_planeta():
    # Leer los datos del CSV
    planet_counts = leer_datos_csv()
    
    # Ordenar los datos para el gráfico
    planet_names = list(planet_counts.keys())
    counts = list(planet_counts.values())
    
    # Crear el gráfico
    plt.figure(figsize=(12, 8))
    plt.bar(planet_names, counts, color='skyblue')
    plt.xlabel('Planeta')
    plt.ylabel('Número de Personajes')
    plt.title('Cantidad de Personajes Nacidos en Cada Planeta')
    plt.xticks(rotation=90)
    plt.tight_layout()  # Ajusta el diseño para evitar el recorte de etiquetas
    plt.show()   

#opcion 6
def obtener_datos_naves(client):
    starships = Starship.list_starships(client)
    datos = {
        'nombre': [],
        'longitud': [],
        'capacidad_carga': [],
        'clasificacion_hiperimpulsor': [],
        'mglt': []
    }
    
    for nave in starships:
        datos['nombre'].append(nave.name)
        datos['longitud'].append(float(nave.length) if nave.length != 'N/A' else 0)
        datos['capacidad_carga'].append(float(nave.cargo_capacity) if nave.cargo_capacity != 'N/A' else 0)
        datos['clasificacion_hiperimpulsor'].append(float(nave.hyperdrive_rating) if nave.hyperdrive_rating != 'N/A' else 0)
        datos['mglt'].append(float(nave.mglt) if nave.mglt != 'N/A' else 0)
    
    return datos

def graficar_caracteristicas_naves(datos):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    # Gráfico de Longitud
    axs[0, 0].barh(datos['nombre'], datos['longitud'], color='blue')
    axs[0, 0].set_title('Longitud de la Nave')
    axs[0, 0].set_xlabel('Longitud (metros)')

    # Gráfico de Capacidad de Carga
    axs[0, 1].barh(datos['nombre'], datos['capacidad_carga'], color='green')
    axs[0, 1].set_title('Capacidad de Carga')
    axs[0, 1].set_xlabel('Capacidad de Carga (kg)')

    # Gráfico de Clasificación de Hiperimpulsor
    axs[1, 0].barh(datos['nombre'], datos['clasificacion_hiperimpulsor'], color='red')
    axs[1, 0].set_title('Clasificación de Hiperimpulsor')
    axs[1, 0].set_xlabel('Clasificación de Hiperimpulsor')

    # Gráfico de MGLT
    axs[1, 1].barh(datos['nombre'], datos['mglt'], color='purple')
    axs[1, 1].set_title('MGLT')
    axs[1, 1].set_xlabel('MGLT')

    plt.tight_layout()
    plt.show()
#opcion 7
def calcular_estadisticas(starships):
    hyperdrive_ratings = []
    mglt_values = []
    max_speeds = []
    costs = []
    
    for starship in starships:
        if starship.hyperdrive_rating != 'N/A':
            try:
                hyperdrive_ratings.append(float(starship.hyperdrive_rating))
            except ValueError:
                continue
        if starship.mglt != 'N/A':
            try:
                mglt_values.append(float(starship.mglt))
            except ValueError:
                continue
        if starship.max_atmosphering_speed != 'N/A':
            try:
                max_speeds.append(float(starship.max_atmosphering_speed))
            except ValueError:
                continue
        if starship.cost_in_credits != 'N/A':
            try:
                costs.append(float(starship.cost_in_credits))
            except ValueError:
                continue

    def calcular_datos(datos):
        return {
            'promedio': statistics.mean(datos) if datos else 'N/A',
            'moda': statistics.mode(datos) if datos else 'N/A',
            'maximo': max(datos, default='N/A'),
            'minimo': min(datos, default='N/A')
        }

    return {
        'hyperdrive_rating': calcular_datos(hyperdrive_ratings),
        'mglt': calcular_datos(mglt_values),
        'max_atmosphering_speed': calcular_datos(max_speeds),
        'cost_in_credits': calcular_datos(costs)
    }
    
def mostrar_estadisticas_naves(client):
    starships = Starship.list_starships(client)
    stats = calcular_estadisticas(starships)
    
    print("\n*** Estadísticas de Naves Espaciales ***\n")
    
    def mostrar_estadisticas(variable_name, stats):
        print(f"{variable_name.capitalize()}:")
        print(f"  Promedio: {stats['promedio']}")
        print(f"  Moda: {stats['moda']}")
        print(f"  Máximo: {stats['maximo']}")
        print(f"  Mínimo: {stats['minimo']}")
        print("-" * 40)
    
    mostrar_estadisticas('Clasificación de Hiperimpulsor', stats['hyperdrive_rating'])
    mostrar_estadisticas('MGLT', stats['mglt'])
    mostrar_estadisticas('Velocidad Máxima en Atmósfera', stats['max_atmosphering_speed'])
    mostrar_estadisticas('Costo en Créditos', stats['cost_in_credits'])

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
    print("4. Buscar Personaje")
    print("5. Grafico de cantidad de personajes nacidos en cada planeta")
    print("6. Graficos de caracteristicas de naves")
    print("7. Estadisticas sobre naves")
    print("8. Construir mision")
    print("9. Visualizar mision")
    print("10. Guardar misiones")
    print("11. Cargar misiones")
    print("12. Salir del programa")
    opcion=input("Escoga el número de la opcion correcta:\n")

    #funcion que verifica la respuesta del usuario, si no es una opcion valida lo devuelve al menu

    if opcion.isnumeric():
        if opcion == "1":
            print("Espere un poco por favor...")
            mostrar_lista_peliculas(client)
            menu()
        elif opcion=="2":
            print("Espere un poco por favor...")
            mostrar_lista_especies(client)
            menu()
        elif opcion=="3":
            print("Espere un poco por favor...")
            mostrar_lista_planetas(client)
            menu()
        elif opcion=="4":
            print("Espere un poco por favor...")
            buscar_personaje(client)
            menu()
        elif opcion=="5":
            print("Espere un poco por favor...")
            obtener_personajes_por_planeta(client)
            graficar_personajes_por_planeta()
            # opcion_5(client)
            menu()
        elif opcion=="6":
            datos_naves = obtener_datos_naves(client)
            graficar_caracteristicas_naves(datos_naves)
            menu()
        elif opcion=="7":
            print("Espere un poco por favor...")
            mostrar_estadisticas_naves(client)
            menu()
        elif opcion=="8":
            print(opcion)
            return True
        elif opcion=="9":
            print(opcion)
            return True
        elif opcion=="10":
            print(opcion)
            return True
        elif opcion=="11":
            print(opcion)
            return True
        elif opcion=="12":
            print(opcion)
            return True
        else:
            print("Debe seleccionar un numero del 1 al 10, vuelva a intentar")
            menu()
    else:
        print("Debe seleccionar un numero del 1 al 10, vuelva a intentar")
        menu()
    
# Crear un cliente SWAPI
client = Conexion() 
menu()
