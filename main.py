import requests

class Conexion:
    #conexion principal a la plataforma swapi
    url_api = "https://www.swapi.tech/api"

    def _init_(self):
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
    def _init_(self, titulo, episodio_id, fecha_lanzamiento, opening_crawl, director):
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

    def _init_(self, name, height, classification, homeworld, language, characters, films):
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
        films_data = client.obtener_todos_datos('films', 'results')
        
        print("Asociando películas con especies...")
        
        for film in films_data:
            film_details = client.obtener_datos(f'films/{film["uid"]}')
            film_title = film_details['title']
            
            print(f"Procesando película: {film_title}")
            
            for species_url in film_details['species']:
                species_id = species_url.split('/')[-1]
                if species_id in Species.species_ids:
                    print(f"Asociando a especie con ID {species_id} ({Species.species_ids[species_id].name})")
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
    def _init_(self, name, rotation_period, orbital_period, population, climate, films, residents):
        self.name = name
        self.rotation_period = rotation_period
        self.orbital_period = orbital_period
        self.population = population
        self.climate = climate
        self.films = films
        self.residents = residents

    
    def from_api_data(cls, data):
        return cls(
            name=data.get('name'),
            rotation_period=data.get('rotation_period'),
            orbital_period=data.get('orbital_period'),
            population=data.get('population'),
            climate=data.get('climate'),
            films=data.get('films', []),
            residents=data.get('residents', [])
        )

    
    def list_planets(client):
        planets_data = client.obtener_todos_datos('planets')
        planets_list = [Planet.from_api_data(planet['properties']) for planet in planets_data]
        return planets_list

    def mostrar_planeta(self):
        print(f"Nombre: {self.name}")
        print(f"Periodo de órbita: {self.orbital_period}")
        print(f"Peíodo de rotación: {self.rotation_period}")
        print(f"Cantidad de habitantes: {self.population}")
        print(f"Tipo de clima: {self.climate}")
        print(f"Episodios en los que aparece: {', '.join(self.films)}")
        print(f"Personajes originarios : {', '.join(self.residents)}")
        print("-" * 40)
        
        
class Character:
    def _init_(self, name, homeworld, gender, species, films, starships, vehicles):
        self.name = name
        self.homeworld = homeworld
        self.gender = gender
        self.species = species
        self.films = films
        self.starships = starships
        self.vehicles = vehicles

    
    def from_api_data(cls, data):
        return cls(
            name=data.get('name'),
            homeworld=data.get('homeworld'),
            gender=data.get('gender'),
            species=data.get('species', []),
            films=data.get('films', []),
            starships=data.get('starships', []),
            vehicles=data.get('vehicles', [])
        )

    
    def search_character(client, query):
        characters_data = client.obtener_todos_datos('people')
        matching_characters = [
            Character.from_api_data(character['properties'])
            for character in characters_data
            if query.lower() in character['properties']['name'].lower()
        ]
        return matching_characters

    def mostrar_personaje(self):
        print(f"Nombre: {self.name}")
        print(f"Nombre del planeta de origen: {self.homeworld}")
        print(f"Genero: {self.gender}")
        print(f"Especie: {', '.join(self.species)}")
        print(f"Titulo de los episodios en los que interviene: {', '.join(self.films)}")
        print(f"Nombre de las nave que utiliza: {', '.join(self.starships)}")
        print(f"Nombre de los vehiculos que utiliza: {', '.join(self.vehicles)}")
        print("-" * 40)
         

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
        
#Aqui definiremos el menu principal
def menu():
    print("")
    print("")
    print("***************** STAR WAR ***********************")
    print("**************** METROPEDIA **********************")
    print("")
    print("")
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
            print(opcion)
            return True
        elif opcion=="4":
            print(opcion)
            return True
        elif opcion=="5":
            print(opcion)
            return True
        elif opcion=="6":
            print(opcion)
            return True
        elif opcion=="7":
            print(opcion)
            return True
        elif opcion=="8":
            print(opcion)
            return True
        elif opcion=="9":
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
