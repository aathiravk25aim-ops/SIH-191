"""24-habitation dataset for SIH26191 (illustrative planning data)."""
import pandas as pd

# location, state, disaster, intensity(0-10), density/km2, affected, shelter, red_lat, red_lon,
# safe hub, green_lat, green_lon, elevation_m, safe_elevation_m, hospitals, schools
_ROWS = [
("Dibrugarh Riverbank","Assam","River flood",9,2400,18000,9000,27.48,94.91,"Chabua Relief Hub",27.47,95.12,105,140,"Assam Medical College,Dibrugarh Civil Hospital","Dibrugarh Govt HS,Kendriya Vidyalaya"),
("Majuli Island","Assam","River erosion",9,1100,12000,5000,26.95,94.17,"Jorhat Safe Ground",26.76,94.20,85,110,"Majuli Civil Hospital","Garmur HS School"),
("Darbhanga Lowlands","Bihar","Flood",8,3200,26000,12000,26.15,85.90,"Madhubani Shelter Complex",26.35,86.07,50,62,"DMCH Darbhanga","Darbhanga Govt School,Zila School"),
("Sundarbans Gosaba","West Bengal","Cyclone surge",9,1000,22000,8000,22.16,88.80,"Basanti Cyclone Centre",22.20,88.67,3,12,"Gosaba Rural Hospital","Gosaba HS"),
("Puri Coast","Odisha","Cyclone",9,2100,30000,20000,19.81,85.83,"Khurda Cyclone Hub",20.18,85.62,5,45,"Puri District Hospital","Puri Govt School,Zilla School"),
("Kendrapara Delta","Odisha","Cyclone surge",8,1500,19000,9000,20.50,86.42,"Cuttack Safe Hub",20.46,85.88,4,30,"Kendrapara DHH","Kendrapara HS"),
("Chennai Adyar","Tamil Nadu","Urban flood",8,6000,40000,16000,13.01,80.25,"Tambaram Relief Camp",12.92,80.12,6,40,"Adyar Govt Hospital,Rajiv Gandhi GH","Adyar Corp School"),
("Nagapattinam Coast","Tamil Nadu","Tsunami / cyclone",8,1800,15000,10000,10.77,79.84,"Thanjavur Safe Zone",10.79,79.14,3,60,"Nagapattinam GH","Nagai Govt HS"),
("Cuddalore Coast","Tamil Nadu","Cyclone",7,1900,14000,9000,11.75,79.77,"Virudhachalam Hub",11.52,79.32,4,55,"Cuddalore GH","Cuddalore Govt School"),
("Kuttanad Wetlands","Kerala","Flood",9,1400,21000,9500,9.40,76.40,"Changanassery Shelter",9.44,76.54,1,15,"Alappuzha Medical College","Kuttanad HS,Govt LP School"),
("Wayanad Hills","Kerala","Landslide",9,450,9000,4500,11.60,76.08,"Kalpetta Safe Hub",11.61,76.08,900,780,"Wayanad Medical College","Meppadi HS"),
("Kozhikode Beach","Kerala","Storm surge",7,4500,17000,9000,11.25,75.77,"Feroke Relief Hub",11.18,75.84,4,28,"Kozhikode Beach Hospital","Govt Model HS"),
("Kedarnath Valley","Uttarakhand","Landslide / GLOF",10,120,6000,2500,30.73,79.07,"Rudraprayag Safe Hub",30.28,78.98,3500,900,"Kedarnath PHC","Guptkashi School"),
("Joshimath Slope","Uttarakhand","Subsidence",9,300,8500,3500,30.55,79.56,"Pipalkoti Hub",30.43,79.43,1890,1300,"Joshimath CHC","Joshimath Inter College"),
("Shimla Ridge","Himachal Pradesh","Landslide",7,2500,11000,6500,31.10,77.17,"Kufri Safe Ground",31.10,77.27,2200,2500,"IGMC Shimla","Govt Sr Sec School"),
("Kinnaur Slopes","Himachal Pradesh","Landslide",8,13,3000,1500,31.58,78.47,"Reckong Peo Hub",31.54,78.27,2800,2600,"Kinnaur Civil Hospital","Peo Govt School"),
("Gangtok Slopes","Sikkim","Landslide",8,300,7500,4000,27.33,88.61,"Ranipool Safe Hub",27.30,88.58,1650,1000,"STNM Hospital","Tashi Namgyal Academy"),
("Leh Cloudburst Zone","Ladakh","Flash flood",8,60,4000,2500,34.16,77.58,"Choglamsar Hub",34.12,77.58,3500,3300,"SNM Hospital Leh","Govt Boys HS Leh"),
("Bhuj Fault Zone","Gujarat","Earthquake",8,950,16000,9000,23.25,69.67,"Anjar Safe Ground",23.11,70.03,110,150,"GK General Hospital","Bhuj Govt School"),
("Surat Tapi Banks","Gujarat","River flood",8,5200,32000,14000,21.17,72.83,"Bardoli Relief Hub",21.12,73.11,13,30,"New Civil Hospital Surat","Surat Municipal School"),
("Mumbai Mithi River","Maharashtra","Urban flood",8,20000,45000,18000,19.07,72.88,"Panvel Relief Complex",18.99,73.12,8,35,"Sion Hospital,KEM","BMC School Kurla"),
("Raigad Landslide","Maharashtra","Landslide",8,400,9500,4500,18.52,73.43,"Mahad Safe Hub",18.08,73.42,200,260,"Mahad Rural Hospital","Mahad Govt School"),
("Jharia Coalfield","Jharkhand","Mine fire / subsidence",8,2800,14000,5500,23.74,86.41,"Belgaria Township",23.77,86.38,200,230,"Jharia Referral Hospital","Jharia Govt School"),
("Rajahmundry Godavari","Andhra Pradesh","River flood",8,1700,20000,10000,17.00,81.78,"Kakinada Relief Hub",16.99,82.24,14,35,"Rajahmundry GH","Govt Jr College"),
]
_COLS = ["location","state","disaster_type","hazard_intensity","population_density","affected_population",
         "shelter_capacity","red_lat","red_lon","green_name","green_lat","green_lon","elevation_m",
         "safe_elevation_m","hospitals","schools"]

def load_dataset() -> pd.DataFrame:
    df = pd.DataFrame(_ROWS, columns=_COLS)
    # Lifeline stock levels (deterministic, varied so different bottlenecks appear)
    for i, c in enumerate(df.index):
        cap = df.at[c, "shelter_capacity"]
        f = [1.4, 0.9, 1.1, 0.6, 1.2, 0.8][i % 6]
        df.at[c, "water_liters_day"] = int(cap * 3 * f)
        df.at[c, "food_packets"] = int(cap * [1.0, 1.3, 0.7, 1.1][i % 4])
        df.at[c, "sanitation_units"] = int(cap / 20 * [1.2, 0.8, 1.0][i % 3])
        df.at[c, "beds_available"] = int(cap / 8 * [1.0, 0.7, 1.5][i % 3])
    return df
