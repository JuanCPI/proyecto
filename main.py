#Aqui definiremos el menu principal
import requests

class Conexion:
    #conexion principal a la plataforma
    url_api = "https://www.swapi.tech/api"

    def __init__(self):
        pass
    #dependiendo de lo qu
    def get_data(self, endpoint):
        url = f"{self.url_api}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('result', {}).get('properties', {})
        else:
            raise Exception(f"Error fetching data from {url}: {response.status_code}")

    def get_all_data(self, endpoint):
        url = f"{self.url_api}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('result', [])
        else:
            raise Exception(f"Error fetching data from {url}: {response.status_code}")


class Film:
    def __init__(self, title, episode_id, release_date, opening_crawl, director):
        self.title = title
        self.episode_id = episode_id
        self.release_date = release_date
        self.opening_crawl = opening_crawl
        self.director = director

    
    def from_api_data(cls, data):
        return cls(
            title=data.get('title'),
            episode_id=data.get('episode_id'),
            release_date=data.get('release_date'),
            opening_crawl=data.get('opening_crawl'),
            director=data.get('director')
        )

    
    def list_films(client):
        films_data = client.get_all_data('films')
        films = [Film.from_api_data(film['properties']) for film in films_data]
        return films

    def mostrar_film(self):
        print(f"Titulo: {self.title}")
        print(f"Número episodio: {self.episode_id}")
        print(f"Fecha de lanzamiento: {self.release_date}")
        print(f"Opening Crawl: {self.opening_crawl}")
        print(f"Director: {self.director}")
        print("-" * 40)
class Species:
    def __init__(self, name, height, classification, homeworld, language, characters, films):
        self.name = name
        self.height = height
        self.classification = classification
        self.homeworld = homeworld
        self.language = language
        self.characters = characters
        self.films = films


    def from_api_data(cls, data):
        return cls(
            name=data.get('name'),
            height=data.get('height'),
            classification=data.get('classification'),
            homeworld=data.get('homeworld'),
            language=data.get('language'),
            characters=data.get('characters', []),
            films=data.get('films', [])
        )


    def list_species(client):
        species_data = client.get_all_data('species')
        species_list = [Species.from_api_data(species['properties']) for species in species_data]
        return species_list

    def mostrar_especie(self):
        print(f"Nombre: {self.name}")
        print(f"Altura: {self.height}")
        print(f"Clasificación: {self.classification}")
        print(f"Nombre planeta de origen: {self.homeworld}")
        print(f"Lengua materna: {self.language}")
        print(f"Personajes que pertenecen a la especia: {', '.join(self.characters)}")
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
        planets_data = client.get_all_data('planets')
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
    def __init__(self, name, homeworld, gender, species, films, starships, vehicles):
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
        characters_data = client.get_all_data('people')
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
        

# Crear un cliente SWAPI
client = Conexion()

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
    opcion=input("Escoga el número de la opcion correcta:\n")

    #funcion que verifica la respuesta del usuario, si no es una opcion valida lo devuelve al menu

    if opcion.isnumeric():
        if opcion == "1":
            print("es 1")
            return True
        elif opcion=="2":
            print(opcion)
            return True
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
    
    
menu()
