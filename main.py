import requests  #libreria para usar las apis
import matplotlib.pyplot as plt #libreria que te ayuda a graficar
import csv #libreria que te ayuda a trabajar con csv
import statistics # libreria que te ayuda a sacar estadisticas

#Clase que realiza la conexion a distintas apis del Swapi
class Conexion:
    #conexion principal a la plataforma swapi
    url_api = "https://www.swapi.tech/api"

    def __init__(self):
        pass
    #dependiendo de la informacion se obtiene el url
    #se recibe el endpoint que se quiera utilizar
    def obtener_datos(self, endpoint):
        url = f"{self.url_api}/{endpoint}"
        response = requests.get(url)
        #verificamos que hacemos la conexion
        if response.status_code == 200:
            return response.json().get('result', {}).get('properties', {})
        else:
            raise Exception(f"No se pudo realizar la conexion {url}: {response.status_code}")
    #hay que tener en cuenta que los resultados de las apis tienen "results" "result"
    def obtener_todos_datos(self, endpoint, key='results'):
        url = f"{self.url_api}/{endpoint}"
        response = requests.get(url)
        #verificamos que hacemos la conexion
        if response.status_code == 200:
            return response.json().get(key, [])
        else:
            raise Exception(f"No se pudo realizar la conexión {url}: {response.status_code}")

#Definimos la clase pelicula segun el enunciado
class Pelicula:
    def __init__(self, titulo, episodio_id, fecha_lanzamiento, opening_crawl, director):
        self.titulo = titulo
        self.episodio_id = episodio_id
        self.fecha_lanzamiento = fecha_lanzamiento
        self.opening_crawl = opening_crawl
        self.director = director
    
    #aqui empleamos los metodos a utilizar en la clase
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
    def lista_peliculas(client):
        films_data = client.obtener_todos_datos('films','result')
        films = [Pelicula.from_api_data(film['properties']) for film in films_data]
        return films
    #forma en que se imprime las peliculas 
    def mostrar_film(self):
        print(f"Titulo: {self.titulo}")
        print(f"Número episodio: {self.episodio_id}")
        print(f"Fecha de lanzamiento: {self.fecha_lanzamiento}")
        print(f"Opening Crawl: {self.opening_crawl}")
        print(f"Director: {self.director}")
        print("-" * 40)
        
#Definimos la clase Species segun el enunciado        
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
        print(f"Altura: {self.height} cm")
        print(f"Clasificación: {self.classification}")
        print(f"Nombre planeta de origen: {self.homeworld}")
        print(f"Lengua materna: {self.language}")
        print(f"Personajes que pertenecen a la especie: {', '.join(self.characters)}")
        print(f"Episodios en los que aparecen: {', '.join(self.films)}")
        print("-" * 40)

#Definimos la clase Planet segun el enunciado       
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
    def from_api_data(cls, data, client):
        film_titles = []
        for film_url in data.get('films', []):
            film_data = client.obtener_datos(film_url.replace(client.url_api + '/', ''))
            if isinstance(film_data, dict) and 'result' in film_data and 'properties' in film_data['result']:
                film_titles.append(film_data['result']['properties'].get('title', 'Desconocido'))

        resident_names = []
        for resident_url in data.get('residents', []):
            resident_data = client.obtener_datos(resident_url.replace(client.url_api + '/', ''))
            if isinstance(resident_data, dict) and 'result' in resident_data and 'properties' in resident_data['result']:
                resident_names.append(resident_data['result']['properties'].get('name', 'Desconocido'))

        return cls(
            name=data.get('name', 'Desconocido'),
            rotation_period=data.get('rotation_period', 'N/A'),
            orbital_period=data.get('orbital_period', 'N/A'),
            population=data.get('population', 'N/A'),
            climate=data.get('climate', 'N/A'),
            films=film_titles,
            residents=resident_names
        )

    @staticmethod
    def list_planets(client):
        planets_data = client.obtener_todos_datos('planets', 'results')
        planets_list = []

        for planet in planets_data:
            planet_url = planet['url'].replace(client.url_api + '/', '')
            planet_details = client.obtener_datos(planet_url)
            if isinstance(planet_details, dict):
                planet_obj = Planet.from_api_data(planet_details, client)
                planets_list.append(planet_obj)
            else:
                print(f"Advertencia: No se pudo obtener detalles para el planeta {planet['name']}")

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
        
#Definimos la clase Character segun el enunciado
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
#Definimos la clase Starship (nave) segun el enunciado
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


#clase de las misiones
class Mision:
    def __init__(self, nombre, planeta_destino, nave):
        self.nombre = nombre
        self.planeta_destino = planeta_destino
        self.nave = nave
        self.armas = []
        self.integrantes = []

    def agregar_arma(self, arma):
        if len(self.armas) < 7:
            self.armas.append(arma)
        else:
            print("No se pueden agregar más de 7 armas.")

    def agregar_integrante(self, integrante):
        if len(self.integrantes) < 7:
            self.integrantes.append(integrante)
        else:
            print("No se pueden agregar más de 7 integrantes.")

    def mostrar_mision(self):
        print(f"Nombre de la misión: {self.nombre}")
        print(f"Planeta destino: {self.planeta_destino}")
        print(f"Nave utilizada: {self.nave}")
        print("Armas:")
        for arma in self.armas:
            print(f" - {arma}")
        print("Integrantes:")
        for integrante in self.integrantes:
            print(f" - {integrante}")
            
##Funciones del menu
# aqui se colocaran las funciones principales que involucran los metodos de las clases
######################################################################################
#opcion 1: 
def mostrar_lista_peliculas(client):
    peliculas = Pelicula.lista_peliculas(client)
    print("\n*** Lista de Películas de la Saga Star Wars ***\n")
    for pelicula in peliculas:
        pelicula.mostrar_film()
######################################################################################        
#opcion 2:
def mostrar_lista_especies(client):
    especies = Species.list_species(client)
    print("\n*** Lista de Especies de la Saga Star Wars ***\n")
    for especie in especies:
        especie.mostrar_especie()
######################################################################################       
# Opción 3 del menú:
def mostrar_lista_planetas(client):
    try:
        planetas = Planet.list_planets(client)
        print("\n*** Lista de Planetas de la Saga Star Wars ***\n")
        if not planetas:
            print("No se encontraron planetas.")
            return
        for planeta in planetas:
            planeta.mostrar_planeta()
    except Exception as e:
        print(f"Se produjo un error al mostrar la lista de planetas: {e}")
######################################################################################   
# Opción 4 del menú:   
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
        
######################################################################################
# Opcion5 del menu:
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
######################################################################################
#opcion 6
def preparar_datos_naves(starships):
    nombres = []
    longitudes = []
    capacidades_carga = []
    clasificaciones_hiperimpulsor = []
    mglt_values = []
    
    for starship in starships:
        nombres.append(starship['name'])
        
        if starship['length'] != 'unknown':
            try:
                longitudes.append(float(starship['length'].replace(',', '')))
            except ValueError:
                longitudes.append(0)
        else:
            longitudes.append(0)

        if starship['cargo_capacity'] != 'unknown':
            try:
                capacidades_carga.append(float(starship['cargo_capacity'].replace(',', '')))
            except ValueError:
                capacidades_carga.append(0)
        else:
            capacidades_carga.append(0)
        
        if starship['hyperdrive_rating'] != 'unknown':
            try:
                clasificaciones_hiperimpulsor.append(float(starship['hyperdrive_rating']))
            except ValueError:
                clasificaciones_hiperimpulsor.append(0)
        else:
            clasificaciones_hiperimpulsor.append(0)
        
        if starship['MGLT'] != 'unknown':
            try:
                mglt_values.append(float(starship['MGLT']))
            except ValueError:
                mglt_values.append(0)
        else:
            mglt_values.append(0)
    
    return nombres, longitudes, capacidades_carga, clasificaciones_hiperimpulsor, mglt_values

# Función para generar los gráficos
def graficar_caracteristicas_naves():
    starships = obtener_datos_naves()
    nombres, longitudes, capacidades_carga, clasificaciones_hiperimpulsor, mglt_values = preparar_datos_naves(starships)

    plt.figure(figsize=(10, 8))

    # Gráfico de Longitud de las Naves
    plt.subplot(2, 2, 1)
    plt.barh(nombres, longitudes, color='skyblue')
    plt.xlabel('Longitud')
    plt.title('Longitud de las Naves')

    # Gráfico de Capacidad de Carga
    plt.subplot(2, 2, 2)
    plt.barh(nombres, capacidades_carga, color='lightgreen')
    plt.xlabel('Capacidad de Carga')
    plt.title('Capacidad de Carga de las Naves')

    # Gráfico de Clasificación de Hiperimpulsor
    plt.subplot(2, 2, 3)
    plt.barh(nombres, clasificaciones_hiperimpulsor, color='lightcoral')
    plt.xlabel('Clasificación de Hiperimpulsor')
    plt.title('Clasificación de Hiperimpulsor de las Naves')

    # Gráfico de MGLT
    plt.subplot(2, 2, 4)
    plt.barh(nombres, mglt_values, color='gold')
    plt.xlabel('MGLT')
    plt.title('MGLT de las Naves')

    plt.tight_layout()
    plt.show()
    
######################################################################################   
#opcion7:
# Obtener todos los datos de las naves espaciales desde la API
def obtener_datos_naves():
    starships = []
    url = "https://swapi.dev/api/starships/"
    
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            starships.extend(data['results'])
            url = data['next']
        else:
            print(f"Error al obtener la lista de naves: {response.status_code}")
            break
    
    return starships

# Calcular estadísticas globales de las naves espaciales
def calcular_estadisticas_globales(starships):
    hyperdrive_ratings = []
    mglt_values = []
    max_speeds = []
    costs = []
    
    for starship in starships:
        # Recopilar datos relevantes
        if starship['hyperdrive_rating'] != 'unknown':
            try:
                hyperdrive_ratings.append(float(starship['hyperdrive_rating']))
            except ValueError:
                continue
        if starship['MGLT'] != 'unknown':
            try:
                mglt_values.append(float(starship['MGLT']))
            except ValueError:
                continue
        if starship['max_atmosphering_speed'] != 'unknown':
            try:
                max_speeds.append(float(starship['max_atmosphering_speed']))
            except ValueError:
                continue
        if starship['cost_in_credits'] != 'unknown':
            try:
                costs.append(float(starship['cost_in_credits']))
            except ValueError:
                continue
    
    # Calcular estadísticas básicas globales
    return {
        'hyperdrive_rating': calcular_datos(hyperdrive_ratings),
        'mglt': calcular_datos(mglt_values),
        'max_atmosphering_speed': calcular_datos(max_speeds),
        'cost_in_credits': calcular_datos(costs)
    }

# Función para calcular el promedio, moda, máximo y mínimo
def calcular_datos(datos):
    resultado = {
        'promedio': statistics.mean(datos) if datos else 'N/A',
        'maximo': max(datos, default='N/A'),
        'minimo': min(datos, default='N/A')
    }

    try:
        resultado['moda'] = statistics.mode(datos)
    except statistics.StatisticsError:
        resultado['moda'] = 'No hay un modo único'

    return resultado

# Mostrar estadísticas globales de las naves espaciales
def mostrar_estadisticas_naves():
    starships = obtener_datos_naves()
    stats_globales = calcular_estadisticas_globales(starships)
    
    print("\n*** Estadísticas Globales de Naves Espaciales ***\n")
    
    mostrar_estadisticas('Clasificación de Hiperimpulsor', stats_globales['hyperdrive_rating'])
    mostrar_estadisticas('MGLT', stats_globales['mglt'])
    mostrar_estadisticas('Velocidad Máxima en Atmósfera', stats_globales['max_atmosphering_speed'])
    mostrar_estadisticas('Costo en Créditos', stats_globales['cost_in_credits'])

# Función para mostrar estadísticas
def mostrar_estadisticas(variable_name, stats):
    print(f"{variable_name.capitalize()}:")
    print(f"  Promedio: {stats['promedio']}")
    print(f"  Moda: {stats['moda']}")
    print(f"  Máximo: {stats['maximo']}")
    print(f"  Mínimo: {stats['minimo']}")
    print("-" * 40)
   
######################################################################################
#opcion 8
def crear_mision():
    nombre = input("Introduce el nombre de la misión: ")
    planeta_destino = input("Introduce el nombre del planeta destino: ")
    nave = input("Introduce el nombre de la nave a utilizar: ")

    mision = Mision(nombre, planeta_destino, nave)

    print("\n--- Selección de armas ---")
    while len(mision.armas) < 7:
        arma = input("Introduce el nombre de un arma (o escribe 'fin' para terminar): ")
        if arma.lower() == 'fin':
            break
        mision.agregar_arma(arma)

    print("\n--- Selección de integrantes ---")
    while len(mision.integrantes) < 7:
        integrante = input("Introduce el nombre de un integrante (o escribe 'fin' para terminar): ")
        if integrante.lower() == 'fin':
            break
        mision.agregar_integrante(integrante)

    return mision
######################################################################################
#opcion 9
def listar_misiones(misiones):
    if not misiones:
        print("No hay misiones disponibles.")
        return

    print("\n--- Lista de misiones ---")
    for idx, mision in enumerate(misiones, 1):
        print(f"{idx}. {mision.nombre} - Destino: {mision.planeta_destino} - Nave: {mision.nave}")

    return int(input("Selecciona el número de la misión que deseas modificar: ")) - 1
def listar_misiones2(misiones):
    if not misiones:
        print("No hay misiones disponibles.")
        return

    print("\n--- Lista de misiones ---")
    for idx, mision in enumerate(misiones, 1):
        print(f"{idx}. {mision.nombre} - Destino: {mision.planeta_destino} - Nave: {mision.nave}")

    return int(input("Selecciona el número de la misión que deseas visualizar: ")) - 1
def modificar_mision(misiones):
    if not misiones:
        print("No hay misiones disponibles para modificar.")
        return

    idx = listar_misiones(misiones)
    if idx < 0 or idx >= len(misiones):
        print("Selección inválida.")
        return

    mision = misiones[idx]
    print(f"\n--- Modificando misión: {mision.nombre} ---")
    
    while True:
        print("\n¿Qué te gustaría modificar?")
        print("1. Nombre de la misión")
        print("2. Planeta de destino")
        print("3. Nave")
        print("4. Armas")
        print("5. Integrantes")
        print("6. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            modificar_nombre_mision(mision)
        elif opcion == '2':
            modificar_planeta_mision(mision)
        elif opcion == '3':
            modificar_nave_mision(mision)
        elif opcion == '4':
            modificar_armas(mision)
        elif opcion == '5':
            modificar_integrantes(mision)
        elif opcion == '6':
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

def modificar_nombre_mision(mision):
    nuevo_nombre = input("Introduce el nuevo nombre de la misión: ")
    mision.nombre = nuevo_nombre
    print(f"Nombre de la misión actualizado a: {mision.nombre}")

def modificar_planeta_mision(mision):
    nuevo_planeta = input("Introduce el nuevo planeta de destino: ")
    mision.planeta_destino = nuevo_planeta
    print(f"Planeta de destino actualizado a: {mision.planeta_destino}")

def modificar_nave_mision(mision):
    nueva_nave = input("Introduce el nuevo nombre de la nave: ")
    mision.nave = nueva_nave
    print(f"Nave actualizada a: {mision.nave}")

def modificar_armas(mision):
    print("\n--- Armas actuales ---")
    for idx, arma in enumerate(mision.armas, 1):
        print(f"{idx}. {arma}")
    
    accion = input("¿Te gustaría (A)gregar o (E)liminar un arma? (A/E): ").lower()
    
    if accion == 'a':
        while len(mision.armas) < 7:
            arma = input("Introduce el nombre del arma (o escribe 'fin' para terminar): ")
            if arma.lower() == 'fin':
                break
            mision.agregar_arma(arma)
    elif accion == 'e':
        eliminar_arma(mision)

def eliminar_arma(mision):
    arma_idx = int(input("Introduce el número del arma que deseas eliminar: ")) - 1
    if 0 <= arma_idx < len(mision.armas):
        mision.armas.pop(arma_idx)
        print("Arma eliminada.")
    else:
        print("Selección no válida.")

def modificar_integrantes(mision):
    print("\n--- Integrantes actuales ---")
    for idx, integrante in enumerate(mision.integrantes, 1):
        print(f"{idx}. {integrante}")
    
    accion = input("¿Te gustaría (A)gregar o (E)liminar un integrante? (A/E): ").lower()
    
    if accion == 'a':
        while len(mision.integrantes) < 7:
            integrante = input("Introduce el nombre del integrante (o escribe 'fin' para terminar): ")
            if integrante.lower() == 'fin':
                break
            mision.agregar_integrante(integrante)
    elif accion == 'e':
        eliminar_integrante(mision)

def eliminar_integrante(mision):
    integrante_idx = int(input("Introduce el número del integrante que deseas eliminar: ")) - 1
    if 0 <= integrante_idx < len(mision.integrantes):
        mision.integrantes.pop(integrante_idx)
        print("Integrante eliminado.")
    else:
        print("Selección no válida.")
        

######################################################################################
#opcion 10
def visualizar_mision(misiones):
    if not misiones:
        print("No hay misiones disponibles para visualizar.")
        return

    idx = listar_misiones2(misiones)
    if idx < 0 or idx >= len(misiones):
        print("Selección inválida.")
        return

    mision = misiones[idx]
    print(f"\n--- Detalles de la misión: {mision.nombre} ---")
    print(f"Planeta de destino: {mision.planeta_destino}")
    print(f"Nave: {mision.nave}")
    print("\nArmas:")
    if mision.armas:
        for idx, arma in enumerate(mision.armas, 1):
            print(f"{idx}. {arma}")
    else:
        print("No se han asignado armas a esta misión.")
    
    print("\nIntegrantes:")
    if mision.integrantes:
        for idx, integrante in enumerate(mision.integrantes, 1):
            print(f"{idx}. {integrante}")
    else:
        print("No se han asignado integrantes a esta misión.")
    

######################################################################################
#opcion 11
def guardar_misiones(misiones, archivo="misiones_guardadas.txt"):
    if not misiones:
        print("No hay misiones disponibles para guardar.")
        return

    with open(archivo, 'w') as file:
        for mision in misiones:
            file.write(f"Nombre de la misión: {mision.nombre}\n")
            file.write(f"Planeta de destino: {mision.planeta_destino}\n")
            file.write(f"Nave: {mision.nave}\n")
            
            file.write("Armas:\n")
            if mision.armas:
                for arma in mision.armas:
                    file.write(f"  - {arma}\n")
            else:
                file.write("  No se han asignado armas a esta misión.\n")
            
            file.write("Integrantes:\n")
            if mision.integrantes:
                for integrante in mision.integrantes:
                    file.write(f"  - {integrante}\n")
            else:
                file.write("  No se han asignado integrantes a esta misión.\n")
            
            file.write("\n" + "="*50 + "\n\n")
    
    print(f"Misiones guardadas exitosamente en el archivo '{archivo}'.")
    
    
######################################################################################   
#Opcion12
def cargar_misiones(archivo="misiones_guardadas.txt"):
    misiones_cargadas = []

    try:
        with open(archivo, 'r') as file:
            contenido = file.read().strip()
            bloques_mision = contenido.split("\n" + "="*50 + "\n\n")

            for bloque in bloques_mision:
                lineas = bloque.strip().split("\n")
                
                nombre_mision = lineas[0].split(": ")[1].strip()
                planeta_destino = lineas[1].split(": ")[1].strip()
                nave = lineas[2].split(": ")[1].strip()
                
                # Crear una nueva instancia de Mision
                mision = Mision(nombre_mision, planeta_destino, nave)
                
                # Cargar armas
                indice_armas = lineas.index("Armas:") + 1
                while indice_armas < len(lineas) and not lineas[indice_armas].startswith("Integrantes:"):
                    arma = lineas[indice_armas].strip().replace("  - ", "")
                    if arma:
                        mision.agregar_arma(arma)
                    indice_armas += 1

                # Cargar integrantes
                indice_integrantes = lineas.index("Integrantes:") + 1
                while indice_integrantes < len(lineas):
                    integrante = lineas[indice_integrantes].strip().replace("  - ", "")
                    if integrante:
                        mision.agregar_integrante(integrante)
                    indice_integrantes += 1

                misiones_cargadas.append(mision)

        print(f"Misiones cargadas exitosamente desde el archivo '{archivo}'.")
        return misiones_cargadas

    except FileNotFoundError:
        print(f"El archivo '{archivo}' no existe. No se pueden cargar misiones.")
    except Exception as e:
        print(f"Se produjo un error al cargar las misiones: {e}")
    
    return misiones_cargadas
######################################################################################
#Aqui definiremos el menu principal y toda la interaccion del programa

misiones = [] 
def menu():
    while True:
        global misiones
        print("**************************************************")
        print("**************************************************")
        print("***************** STAR WARS **********************")
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
        print("8. Construir misión")
        print("9. Modificar misión")
        print("10. Visualizar misión")
        print("11. Guardar misiones")
        print("12. Cargar misiones")
        print("13. Salir del programa")
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
                # opcion_5(client) #crea el csv pero no pudimos graficarlo
                menu()
            elif opcion=="6":
                print("Espere un poco por favor...")
                graficar_caracteristicas_naves()
                menu()
            elif opcion=="7":
                print("Espere un poco por favor...")
                mostrar_estadisticas_naves()
                menu()
            elif opcion=="8":
                mision = crear_mision()
                misiones.append(mision)
                print("\n--- Detalles de la misión ---")
                mision.mostrar_mision()
                menu()
            elif opcion=="9":
                if misiones:
                    modificar_mision(misiones)
                else:
                    print("No hay misiones disponibles para modificar.")
                menu()
            elif opcion=="10":
                if misiones:
                    visualizar_mision(misiones)
                else:
                    print("No hay misiones disponibles para visualizar.")
                menu()
            elif opcion=="11":
                guardar_misiones(misiones)
                menu()
            elif opcion=="12":
                misiones_cargadas = cargar_misiones()
                if misiones_cargadas:
                    misiones = misiones_cargadas  # Reemplaza las misiones en memoria con las cargadas
                else:
                    print("No se cargaron nuevas misiones.")
                menu()
            elif opcion=="13":
                print("Saliendo de metropedia...Vuelva pronto")
                exit()
            else:
                print("Debe seleccionar un numero del 1 al 10, vuelva a intentar")
                menu()
        else:
            print("Debe seleccionar un numero del 1 al 10, vuelva a intentar")
            menu()
        
# Crear un cliente SWAPI
client = Conexion()
#llamamos al menu
menu()
