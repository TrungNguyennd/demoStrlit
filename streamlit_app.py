import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import math
import json
import altair as alt
import plotly.express as px
import pydeck as pdk

# Page configuration
st.set_page_config(
    page_title="Atlas Dân số Hà Nội",
    page_icon="👨‍👩‍👧‍👧",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# CSS styling
st.markdown("""
<style>
[data-testid="block-container"] {
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
</style>
""", unsafe_allow_html=True)

# Load data
df_reshaped = pd.read_csv('data/population_hanoi.csv')
DATA_URL = "data/hanoi.geojson"
json = pd.read_json(DATA_URL)


def main():
    # Bước 1: Import tệp YAML vào script
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Bước 2: Tạo đối tượng Authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    # Bước 3: Hiển thị widget đăng nhập
    fields = ['username', 'password']

    # Hiển thị widget đăng nhập ngay khi trang web được tải
    name, authentication_status, username = authenticator.login('main', fields=fields)
    def hash_password(password):
    # Thực hiện băm mật khẩu, bạn có thể sử dụng thuật toán băm an toàn như bcrypt
     hashed_password = hashlib.sha256(password.encode()).hexdigest()
     return hashed_password
    # Bước 4: Xử lý kết quả đăng nhập và hiển thị nội dung tương ứng
    if authentication_status:
        st.sidebar.title('👨‍👩‍👧‍👧 Atlas Dân số Hà Nội')

        year_list = list(df_reshaped.year.unique())[::-1]
        indicator_list = ["Tốc độ tăng dân số bình quân (%)", "Tốc độ tăng dân số tự nhiên (%)", "Tốc độ tăng dân số cơ học (%)", "Mật độ dân số (người/km2)", "Số trẻ sinh (người)","Tỷ suất sinh", "Số sinh 3+", "Tỷ lệ trẻ 3+", "Tỷ lệ sàng lọc trước sinh (%)", "Tỷ lệ sàng lọc sơ sinh (%)", "Tỷ số giới tính khi sinh (số trẻ trai/100 trẻ gái)"]
        indicator_list_key = ["rate", "rate_growth", "rate_mechanical", "density", "born", "birth_rate", "born_3", "born_per_3", "prenatal_screening", "newborn_screening", "m_to_f"]
        selected_indicator = st.sidebar.selectbox('Tiêu chí', indicator_list)
        selected_year = st.sidebar.selectbox('Năm', year_list)
        df_selected_year = df_reshaped[df_reshaped.year == selected_year]
        df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)
        df_selected_year_rate_sorted = df_selected_year.sort_values(by="rate", ascending=False)

        color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
        selected_color_theme = st.sidebar.selectbox('Màu sắc trình bày biểu đồ', color_theme_list)
        st.session_state['authentication_status'] = True
        st.sidebar.button("Logout", on_click=authenticator.logout, args=('Logout', 'main'))
        show_reset_password_form = st.sidebar.button("Reset Password")
        show_Forgot_password_form = st.sidebar.button("Forgot Password")
        show_Forgot_Username_form = st.sidebar.button("Forgot Username")

        if show_Forgot_Username_form:
         st.title('Forgot Username')
         email = st.text_input('Enter your email:')
         reset_button_key = 'reset_button_' + email  # Tạo khóa duy nhất cho nút
         if st.button('Forgot Username', key=reset_button_key):
           try:
             username_forgot_username, email_forgot_username = authenticator.forgot_username(email)
             if username_forgot_username:
                st.success('Username sent securely')
                st.info(f'Username: {username_forgot_username}')  # Gửi thông tin này một cách an toàn đến người dùng
             else:
                st.error('Email not found')
           except Exception as e:
            st.error(e)
            
        if show_Forgot_password_form:
            st.title('Forgot Password')
            username = st.text_input('Enter your username:') 
            reset_button_key = 'reset_button_' + username
            if st.button('Reset Password',key=reset_button_key):
                try:
                  username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password(username)
                  if username_forgot_pw:
                    st.success('New password sent securely')
                    st.info(f'Random password: {random_password}')  # Send this securely to the user
                  elif username_forgot_pw is False:
                    st.error('Username not found')
                except Exception as e:
                   st.error(e)

        if show_reset_password_form:
          with st.form("reset_password_form"):
           current_password = st.text_input("Nhập mật khẩu cũ", type="password")
           new_password = st.text_input("Nhập mật khẩu mới", type="password")
           confirm_password = st.text_input("Xác nhận mật khẩu mới của bạn", type="password")
          

            # Sử dụng nút Submit thay vì button
           submitted = st.form_submit_button("Lưu")

          # Kiểm tra khi nút "Lưu" được nhấp
           if submitted:
            # Thực hiện kiểm tra mật khẩu cũ và xử lý đặt lại mật khẩu
            try:
                reset_result = authenticator.reset_password(
                    username,
                    fields={'current_password': current_password, 'new_password': new_password}
                )

                if reset_result:
                    # Băm mật khẩu mới trước khi cập nhật vào cả tệp YAML và trong đối tượng Authenticator
                    hashed_new_password = hash_password(new_password)
                    config['credentials']['usernames'][username]['password'] = hashed_new_password
                    authenticator.credentials['usernames'][username]['password'] = hashed_new_password

                    # Lưu vào tệp YAML
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file)

                    st.success("Đặt lại mật khẩu thành công!")
                else:
                    st.error("Mật khẩu cũ không đúng hoặc mật khẩu mới không khớp. Vui lòng thử lại.")
            except Exception as e:
                st.error(f"Có lỗi xảy ra khi đặt lại mật khẩu: {e}")
        # Nội dung chi tiết của trang sau khi đăng nhập thành công
        def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
         heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Năm", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
         # height=300
         return heatmap
        def find_indicator_key_selected():
          if selected_indicator in indicator_list:
           return indicator_list_key[indicator_list.index(selected_indicator)]
          else:
           return ""
        # Choropleth map
        def make_choropleth(input_df, input_id, input_column, input_color_theme):
          attribute = find_indicator_key_selected()
          for feature in json["features"]:
            districid = feature["properties"]["district_code"]
            dataDistrict = input_df[input_df.district_code == districid]
            feature["properties"]["population"] = dataDistrict["population"].values[0]
            feature["properties"][attribute] = dataDistrict[attribute].values[0]
          df_JSON = pd.DataFrame()
          # Custom color scale
          COLOR_RANGE = [
           [247, 194, 207],
           [245, 161, 182],
           [244, 129, 157],
           [242, 97, 132],
           [241, 65, 108]
        ]
          max_population = json["features"].apply(lambda row: row["properties"]["population"]).max()
          print('hdjfhdjfh')
          print(max_population)
          # Tính giá trị của BREAKS tùy thuộc vào giá trị tối đa của population
          BREAKS = [max_population * i / 5 for i in range(1, 6)]
          print(BREAKS)
          def calculate_elevation(val):
           return math.sqrt(val) * 10

          # Parse the geometry out in Pandas
          df_JSON["coordinates"] = json["features"].apply(lambda row: row["geometry"]["coordinates"])
          df_JSON["name"] = json["features"].apply(lambda row: row["properties"]["name"])
          df_JSON["population"] = json["features"].apply(lambda row: row["properties"]["population"])
          df_JSON[attribute] = json["features"].apply(lambda row: row["properties"][attribute])
          df_JSON["elevation_population"] = json["features"].apply(lambda row: calculate_elevation(row["properties"]["population"]))
    
          # Tính toán giá trị màu sắc tương ứng cho population
          def get_fill_color_population(value):
            for i, b in enumerate(BREAKS):
               if value < b:
                  return COLOR_RANGE[i]
            return COLOR_RANGE[-1]

          df_JSON["fill_color_population"] = df_JSON["population"].apply(get_fill_color_population)
          # Set up PyDeck for PolygonLayer with Tooltip
          polygon_layer = pdk.Layer(
           "PolygonLayer",
           df_JSON,
           id="geojson_population",
           opacity=0.6,
           stroked=False,
           get_polygon="coordinates",
           filled=True,
           wireframe=True,
           get_elevation="elevation_population",
           get_fill_color="fill_color_population",
           get_line_color=[255, 255, 255],
           elevation_scale=0, 
           extruded=False, 
           pickable=True,
          )
    
          tooltip = {"html": "<b>Quận/huyện:</b> {name} <br /><b>Dân số (nghìn người):</b> {population}<br /><b>"+selected_indicator+":</b> {"+attribute+"}"}

         # Set up PyDeck for Map with the PolygonLayer
          map_deck = pdk.Deck(
           layers=[polygon_layer],
           tooltip=tooltip,
           initial_view_state=pdk.ViewState(
               latitude=21.0285, longitude=105.8542, zoom=8, maxZoom=16, pitch=0.0, bearing=0
           ),
          effects=[
             {
                "@@type": "LightingEffect",
                "shadowColor": [0, 0, 0, 0.5],
                "ambientLight": {"@@type": "AmbientLight", "color": COLOR_RANGE[0], "intensity": 1.0},
                "directionalLights": [
                    {"@@type": "_SunLight", "timestamp": 1564696800000, "color": COLOR_RANGE[0], "intensity": 1.0, "_shadow": True}
                ],
             }
          ],
          height=300,
           )
          return map_deck
        # Calculation year-over-year population migrations
        def calculate_population_difference(input_df, input_year):
          selected_year_data = input_df[input_df['year'] == input_year].reset_index()
          previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
          selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
          return pd.concat([selected_year_data.district, selected_year_data.id, selected_year_data.population, selected_year_data.population_difference], axis=1).sort_values(by="population_difference", ascending=False)
        def calculate_province_population_growth(data, province, year):
         # Chuyển đổi cột 'year' sang kiểu số nguyên nếu chưa phải
         data['year'] = data['year'].astype(int)

         # Nhóm dữ liệu theo 'province' và 'year', tính tổng dân số
         province_data = data.groupby(['province', 'year'])['population'].sum().reset_index()
    
          # Lọc dữ liệu cho tỉnh và năm cụ thể
         selected_data = province_data[(province_data['province'] == province) & (province_data['year'] == int(year))]

         # Kiểm tra xem có dữ liệu cho tỉnh và năm cụ thể không
         if selected_data.empty:
          raise ValueError(f"No data found for {province} in the year {year}.")

         # Tính tỷ lệ tăng so với năm trước nếu có, ngược lại trả về ký tự '-'
         previous_year_data = province_data[(province_data['province'] == province) & (province_data['year'] == int(year) - 1)]
         population_current_year = selected_data['population'].values[0]


         if not previous_year_data.empty:
            population_current_year = selected_data['population'].values[0]
            population_previous_year = previous_year_data['population'].values[0]
            population_growth_rate = round(population_current_year - population_previous_year,3)
         else:
            population_growth_rate = '-'
         return population_current_year, population_growth_rate
        def calculate_province_rate_growth(data, province, year):
          # Chuyển đổi cột 'year' sang kiểu số nguyên nếu chưa phải
         data['year'] = data['year'].astype(int)

         attribute = find_indicator_key_selected()
         # Nhóm dữ liệu theo 'province' và 'year', tính tổng dân số
         province_data = data.groupby(['province', 'year'])[attribute].sum().reset_index()

         # Lọc dữ liệu cho tỉnh và năm cụ thể
         selected_data = province_data[(province_data['province'] == province) & (province_data['year'] == int(year))]

          # Kiểm tra xem có dữ liệu cho tỉnh và năm cụ thể không
         if selected_data.empty:
           raise ValueError(f"No data found for {province} in the year {year}.")

         # Tính tỷ lệ tăng so với năm trước nếu có, ngược lại trả về ký tự '-'
         previous_year_data = province_data[(province_data['province'] == province) & (province_data['year'] == int(year) - 1)]
         rate_current_year = selected_data[attribute].values[0]


         if not previous_year_data.empty:
          rate_current_year = selected_data[attribute].values[0]
          rate_previous_year = previous_year_data[attribute].values[0]
          rate_growth_rate = rate_current_year - rate_previous_year
         else:
          rate_growth_rate = '-'
         return rate_current_year, rate_growth_rate
        #######################
        # Dashboard Main Panel
        col = st.columns((1.5, 4.5, 2), gap='medium')
        with col[0]:
         st.markdown('#### Dân số ' + str(selected_year))
         df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)
         result = calculate_province_population_growth(df_reshaped, 1, selected_year)
         result_rate = calculate_province_rate_growth(df_reshaped, 1, selected_year)
         first_state_name = 'Dân số trung bình (nghìn người)'
         first_state_population = result[0]
         first_state_delta = result[1]
         st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

         last_state_name = selected_indicator
         last_state_population = round(result_rate[0]/30,1)
         if result_rate[1] != '-':
          last_state_delta = round(result_rate[1]/30,1)
         else:
          last_state_delta = '-'
        
         st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

         st.markdown('#### ' + selected_indicator + " " + str(selected_year))
         attribute = find_indicator_key_selected()
         df_selected_sorted = df_selected_year.sort_values(by=attribute, ascending=False)
         st.dataframe(df_selected_sorted,
                 column_order=("district", attribute),
                 hide_index=True,
                 width=None,
                 use_container_width=True,
                 column_config={
                    "district": st.column_config.TextColumn(
                        "Quận/huyện",
                    ),
                    attribute: st.column_config.ProgressColumn(
                        "Giá trị",
                        format="%f",
                        width=None,
                        min_value=min(df_selected_sorted[attribute]),
                        max_value=max(df_selected_sorted[attribute]),
                     )}
                 )
         
        with col[1]:
         st.markdown('#### Bản đồ dân số Hà Nội ' + str(selected_year))
         map_deck = make_choropleth(df_selected_year, 'district_code', 'population', selected_color_theme)
         st.pydeck_chart(map_deck)

         heatmap = make_heatmap(df_reshaped, 'year', 'district', 'population', selected_color_theme)
         st.altair_chart(heatmap, use_container_width=True)
        with col[2]:
         st.markdown('#### Dân số theo quận/huyện ' + str(selected_year))

         st.dataframe(df_selected_year_sorted,
                 column_order=("district", "population"),
                 hide_index=True,
                 width=None,
                 use_container_width=True,
                 column_config={
                    "district": st.column_config.TextColumn(
                        "Quận/huyện",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Dân số (người)",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.population),
                     )}
                 )

         with st.expander('Thông tin', expanded=True):
          st.write('''
            - Nguồn dữ liệu: [CHI CỤC DÂN SỐ - KẾ HOẠCH HÓA GIA ĐÌNH HÀ NỘI](https://dskhhgdhanoi.gov.vn/).
            - :orange[**Chỉ tiêu dân số**]: Atlas điện tử cung cấp các số liệu về chỉ tiêu dân số như mật độ, tỷ lệ tăng dân số tự nhiên, mật độ và nhiều tiêu chí khác tại các quận/huyện trên địa bàn Thành phố Hà Nội từ năm 2014 đến 2023
            - Phát triển bởi: [eKMap](https://ekgis.com.vn/)
            ''')

        # Bước 6: Kiểm tra thông tin đăng nhập và lưu trữ vào session state
        st.session_state['authenticated'] = True
        st.session_state['username'] = username
        st.session_state['name'] = name

        # Bước 7: Hiển thị mã JavaScript để chuyển hướng
        st.markdown('<script> window.location.href = "/streamlit_app.py" </script>', unsafe_allow_html=True)
    else:
        # Hiển thị thông báo lỗi khi tên đăng nhập hoặc mật khẩu không đúng
        st.error("Nhập username và password")
# Thực thi hàm main khi tệp được chạy
if __name__ == '__main__':
    main()
