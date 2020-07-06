import csv
from django.contrib.gis.geos import fromstr
from pathlib import Path
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from make_model.models import Shop, Category, Comment, ShopImage, District

# from .model import *

file = '/home/giacat/Documents/my_model/Comment.csv'
store = '/home/giacat/Documents/my_model/Item.csv'
image = '/home/giacat/Documents/my_model/Image.csv'
arr_cate = []
arr_user = []
arr_dist = ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 4', 'Quận 5', 'Quận 6', 'Quận 7', 'Quận 8', 'Quận 9', 'Quận 10', 'Quận 11', 'Quận 12', 'Quận Bình Thạnh', 'Quận Bình Tân', 'Quận Gò Vấp', 'Quận Phú Nhuận', 'Quận Thủ Đức', 'Quận Tân Bình', 'Quận Tân Phú', 'Bình Chánh', 'Củ Chi', 'Hóc Môn', 'Nhà Bè']


def get_category_arr():
    data_cate = csv.reader(open(store, encoding='utf-8', errors='ignore'), delimiter=",")
    for r in data_cate:
        for cate in r[4].split(','):
            if cate.strip() not in arr_cate:
                ct = Category()
                ct.category = cate.strip()
                ct.save()
                arr_cate.append(cate.strip())
            else:
                pass

def load_district():
    for dist in arr_dist:
        dt = District()
        dt.district = dist
        dt.save()

def load_store():
    data_store = csv.reader(open(store, encoding='utf-8', errors='ignore'),delimiter=",")
    for row in data_store:
        st = Shop()
        st.id = row[0]
        st.name = row[1]
        st.slug = row[14]
        st.cover_img = row[2]
        st.avgscore = row[5]
        if row[6] == '':
            st.review_count = 0
        else:
            st.review_count = int(row[6])
        st.address = row[7]
        if row[8].strip() in arr_dist:
            st.district_id = int(arr_dist.index(row[8])+1)
        else:
            pass 
        st.city = row[9]
        st.lat = row[10]
        st.lon = row[11]
        st.location = fromstr(f'POINT({row[11]} {row[10]})', srid=4326)
        st.timeopen = row[12]
        st.pricerange = row[13]
        st.save()
        for c in row[4].split(','):
            if c.strip() in arr_cate:
                st.category.add(int(arr_cate.index(c.strip()) + 1))
            else:
                pass


def load_user():
    data = csv.reader(open(file, encoding='utf-8', errors='ignore'), delimiter=",")

    for row in data:
        if row[0] != "Number":
            # Post.id = row[0]
            if (row[8] not in arr_user) and (len(row[2]) < 150):
                post = User()
                post.password = "thanhduy66"
                post.last_login = "2018-09-27 05:51:42.521991"
                post.is_superuser = "0"
                post.username = row[8]
                post.first_name = ""
                post.email = ""
                post.is_staff = "0"
                post.is_active = "1"
                post.date_joined = "2018-09-27 05:14:50"
                post.last_name = row[2]
                post.save()
                arr_user.append(row[8])
            else:
                pass


def load_cmts():
    data = csv.reader(open(file, encoding='utf-8', errors='ignore'), delimiter=",")
    for row in data:
        if len(row[2]) < 150:
            cmt = Comment()
            cmt.shop_id = int(row[7])
            cmt.author_id = arr_user.index(row[8]) + 2
            cmt.body = row[6]
            cmt.rating = row[5]
            cmt.save()


def load_image():
    data_image = csv.reader(open(image, encoding='utf-8', errors='ignore'), delimiter=",")
    for row in data_image:
        img = ShopImage()
        img.img_url = row[1]
        img.shop_id = int(row[3])
        img.save()

def run():
    get_category_arr()
    print('Loading data')
    load_district()
    print('+ District')
    load_store()
    print('+ Store & Category')
    load_user()
    print('+ Users')
    load_cmts()
    print('+ Comments')
    load_image()
    print('+ Images')
