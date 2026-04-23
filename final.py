import requests
import math
import folium
import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Cấu hình các đường dẫn API
OPEN_STREET_MAP_URL = "https://nominatim.openstreetmap.org/search"
OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("OPENWEATHER_API_KEY")

OVERPASS_SERVERS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách đường chim bay giữa 2 tọa độ (bằng km)"""
    R = 6371  # Bán kính trái đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def get_coordinates(city_name):
    """Bước 1: Lấy tọa độ từ tên thành phố"""
    params = {"q": city_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "TDTTHCMUS_Project/1.0"}
    try:
        response = requests.get(url=OPEN_STREET_MAP_URL, params=params, headers=headers)
        data = response.json()
        if len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Lỗi Bước 1: {e}")
    return None, None

def get_weather(lat, lon):
    """Bước 2: Lấy thông tin thời tiết (Thêm việc lấy icon code cho bước 5)"""
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    try:
        response = requests.get(OPEN_WEATHER_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            icon_code = data["weather"][0]["icon"] # Lấy mã icon
            return temp, desc, icon_code
    except Exception as e:
        print(f"Lỗi Bước 2: {e}")
    return None, None, None

def get_nearby_parks(lat, lon):
    """Bước 3: Tìm công viên và tọa độ của chúng để vẽ bản đồ"""
    query = f'[out:json][timeout:25];(node["leisure"="park"](around:1000,{lat},{lon});way["leisure"="park"](around:1000,{lat},{lon}););out center;'
    headers = {'User-Agent': 'TDTTHCMUS_Project/1.0'}

    for url in OVERPASS_SERVERS:
        try:
            response = requests.get(url, params={'data': query}, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                parks = {}
                for element in data.get('elements', []):
                    name = element.get('tags', {}).get('name')
                    # Lấy tọa độ (node thì dùng lat/lon, way thì dùng center)
                    p_lat = element.get('lat') or element.get('center', {}).get('lat')
                    p_lon = element.get('lon') or element.get('center', {}).get('lon')
                    
                    if name and p_lat and p_lon:
                        parks[name] = (p_lat, p_lon) # Lưu theo dict để lọc trùng tên
                return parks
        except:
            continue
    return {}

# def draw_map(city_name, lat, lon, temp, condition, icon_code, parks):
#     """Bước 5: Vẽ bản đồ hiển thị kết quả"""
#     # Khởi tạo bản đồ tại vị trí trung tâm
#     m = folium.Map(location=[lat, lon], zoom_start=14)
    
#     # Tạo icon thời tiết từ OpenWeather
#     weather_icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
#     weather_icon = folium.features.CustomIcon(weather_icon_url, icon_size=(50, 50))
    
#     # Đánh dấu vị trí trung tâm
#     folium.Marker(
#         [lat, lon],
#         popup=f"<b>{city_name}</b><br>Nhiệt độ: {temp}°C<br>Thời tiết: {condition}",
#         icon=weather_icon, # Hiển thị icon thời tiết
#         tooltip="Trung tâm thành phố"
#     ).add_to(m)
    
#     # Đánh dấu các công viên và vẽ đường nối tính khoảng cách
#     for name, coords in parks.items():
#         p_lat, p_lon = coords
#         distance = calculate_distance(lat, lon, p_lat, p_lon)
        
#         # Điểm đánh dấu công viên
#         folium.Marker(
#             [p_lat, p_lon],
#             popup=f"<b>{name}</b><br>Cách trung tâm: {distance} km",
#             icon=folium.Icon(color="green", icon="tree", prefix='fa'),
#             tooltip=name
#         ).add_to(m)
        
#         # Vẽ đường nối từ trung tâm đến công viên
#         folium.PolyLine(
#             locations=[[lat, lon], [p_lat, p_lon]],
#             color="blue",
#             weight=2,
#             opacity=0.6,
#             dash_array='5' # Vẽ nét đứt
#         ).add_to(m)
        
#     # Lưu bản đồ ra file HTML
#     output_file = f"map_{city_name.replace(' ', '_')}.html"
#     m.save(output_file)
#     print(f"\n=> [Thành công] Đã tạo bản đồ tại file: {output_file}")
#     print("=> Mở file HTML này bằng trình duyệt web (Chrome, Edge...) để xem bản đồ.")

def draw_map(city_name, lat, lon, temp, condition, icon_code, parks):
    """Bước 5: Vẽ bản đồ hiển thị kết quả"""
    # Khởi tạo bản đồ tại vị trí trung tâm
    m = folium.Map(location=[lat, lon], zoom_start=14)
    
    # URL của icon thời tiết (dùng HTTPS)
    weather_icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    
    # In ra URL ở console để bạn test link có hoạt động không
    print(f"[*] Link icon thời tiết: {weather_icon_url}")

    # Chèn icon trực tiếp vào Popup bằng mã HTML (Cách này 100% hoạt động)
    popup_html = f"""
    <div style="text-align: center; font-family: Arial;">
        <b style="font-size: 16px;">{city_name}</b><br>
        <img src="{weather_icon_url}" alt="weather" width="60" height="60"><br>
        Nhiệt độ: {temp}°C<br>
        Thời tiết: {condition}
    </div>
    """
    
    # Gắn CustomIcon (vẫn thử gắn lên marker như cũ)
    weather_icon = folium.CustomIcon(weather_icon_url, icon_size=(50, 50))

    # Đánh dấu vị trí trung tâm
    folium.Marker(
        [lat, lon],
        popup=folium.Popup(popup_html, max_width=250), # Sử dụng Popup HTML vừa tạo
        icon=weather_icon, 
        tooltip="Click để xem thời tiết thành phố"
    ).add_to(m)
    
    # Đánh dấu các công viên và vẽ đường nối tính khoảng cách
    for name, coords in parks.items():
        p_lat, p_lon = coords
        distance = calculate_distance(lat, lon, p_lat, p_lon)
        
        # Điểm đánh dấu công viên
        folium.Marker(
            [p_lat, p_lon],
            popup=f"<b>{name}</b><br>Cách trung tâm: {distance} km",
            icon=folium.Icon(color="green", icon="tree", prefix='fa'),
            tooltip=name
        ).add_to(m)
        
        # Vẽ đường nối từ trung tâm đến công viên
        folium.PolyLine(
            locations=[[lat, lon], [p_lat, p_lon]],
            color="blue",
            weight=2,
            opacity=0.6,
            dash_array='5' # Vẽ nét đứt
        ).add_to(m)
        
    # Lưu bản đồ ra file HTML
    output_file = f"map_{city_name.replace(' ', '_')}.html"
    m.save(output_file)
    print(f"\n=> [Thành công] Đã tạo bản đồ tại file: {output_file}")
    print("=> Mở file HTML này bằng trình duyệt web (Chrome, Edge...) để xem bản đồ.")

def main():
    city_input = input("Nhập tên thành phố: ")
    
    lat, lon = get_coordinates(city_input)
    
    if lat and lon:
        temp, condition, icon_code = get_weather(lat, lon)
        parks = get_nearby_parks(lat, lon)
        
        # Bước 4: Hiển thị kết quả lên Console
        print("\n" + "="*30)
        print(f"City: {city_input}")
        print(f"Coordinates: ({lat}, {lon})")
        print("-" * 10)
        print("Weather:")
        if temp is not None:
            print(f"  Temperature: {temp}°C")
            print(f"  Condition: {condition}")
        else:
            print("  Không lấy được dữ liệu thời tiết.")
        
        print("-" * 10)
        print("Nearby places:")
        if parks:
            for i, (name, coords) in enumerate(parks.items(), 1):
                print(f"  {i}. {name}")
        else:
            print("  Không tìm thấy công viên nào trong bán kính 1km.")
        print("="*30)
        
        # Thực thi Bước 5
        if temp is not None:
             draw_map(city_input, lat, lon, temp, condition, icon_code, parks)
            
    else:
        print("Không tìm thấy tọa độ cho thành phố này. Vui lòng thử lại!")

if __name__ == "__main__":
    main()