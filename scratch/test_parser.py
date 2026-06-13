import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Helper to normalize headers to SQLite safe names
def get_safe_col_name(header):
    import re
    # Remove accents
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỊịỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    res = []
    for c in header:
        idx = s1.find(c)
        if idx != -1:
            res.append(s0[idx])
        else:
            res.append(c)
    no_accent = "".join(res)
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', no_accent)
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned.strip('_')

# Load mock JSON
with open("scratch/detail_TKQLMB8Q.json", "r", encoding="utf-8") as f:
    res = json.load(f)

detail_data = res.get("data", {})

# Extract values
tk_id = detail_data.get("id")
ma_hang = detail_data.get("code")
tinh = detail_data.get("district", {}).get("provinceName", "TP Hồ Chí Minh")
quan = detail_data.get("district", {}).get("name", "")
phuong = detail_data.get("ward", {}).get("name", "")
duong = detail_data.get("street", {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
ngo_so_nha = detail_data.get("address", "")
phan_loai = ", ".join([c.get("name") for c in detail_data.get("criteria", []) if c.get("name")])

# Construct Noi_dung_chinh
noi_dung_chinh = f"{ngo_so_nha} {duong}, {detail_data.get('area', '')}m2, {detail_data.get('floors', '')} tầng, mt {detail_data.get('wide', '')}m, sâu {detail_data.get('depth', '')}m, giá {detail_data.get('offeringPrice', '')} tỷ, Phường {phuong} {quan}"

mo_ta_chi_tiet = detail_data.get("description", "")
gia_chao = str(detail_data.get("offeringPrice", ""))
dt_thuc_te = str(detail_data.get("actualArea", ""))
dt_tren_so = str(detail_data.get("area", ""))
so_tang = str(detail_data.get("floors", ""))
mat_tien = str(detail_data.get("wide", ""))
chieu_dai = str(detail_data.get("depth", ""))
so_phong_ngu = str(detail_data.get("bedrooms") or "")
so_nha_ve_sinh = str(detail_data.get("restrooms") or "")
huong = detail_data.get("direction", "")
duong_truoc_nha = str(detail_data.get("minimumRoadWidth") or "")
trang_thai = detail_data.get("status", "")
loai_hop_dong = detail_data.get("contractType", "")

ten_chu_nha = ", ".join([o.get("name") for o in detail_data.get("homeOwner", []) if o.get("name")])
dien_thoai_1 = detail_data.get("contactPhoneNumber", "")

dt_dau_chu = detail_data.get("ownerSideUser", {}).get("phone", "")
ten_dau_chu = detail_data.get("ownerSideUser", {}).get("name", "")
link_fb = detail_data.get("ownerSideUser", {}).get("fbLink", "")

# Extract images
media = detail_data.get("media", [])
property_images = []
sodo_images = []

for m in media:
    m_type = m.get("type")
    m_url = m.get("url")
    if not m_url:
        continue
    if m_type in ["parcel_map", "certificate_image"]:
        sodo_images.append(m_url)
    elif m_type in ["property_image"]:
        property_images.append(m_url)
        
# Fallback to checkin_image if no property_images
if not property_images:
    for m in media:
        if m.get("type") == "checkin_image" and m.get("url"):
            property_images.append(m.get("url"))

print("=== PARSED VALUES FOR TKQLMB8Q ===")
print("tk_id:", tk_id)
print("Ma Hàng:", ma_hang)
print("Tỉnh:", tinh)
print("Quận:", quan)
print("Phường:", phuong)
print("Đường:", duong)
print("Ngõ/Số nhà:", ngo_so_nha)
print("Phân loại:", phan_loai[:100] + "...")
print("Nội dung chính:", noi_dung_chinh)
print("Giá chào:", gia_chao)
print("DT Thực tế:", dt_thuc_te)
print("DT Trên sổ:", dt_tren_so)
print("Số Tầng:", so_tang)
print("Mặt Tiền:", mat_tien)
print("Chieu_dai:", chieu_dai)
print("Số phòng ngủ:", so_phong_ngu)
print("Số nhà vệ sinh:", so_nha_ve_sinh)
print("Tên Chủ Nhà:", ten_chu_nha)
print("Điện thoại Đầu Chủ:", dt_dau_chu)
print("Tên Đầu Chủ (Hợp đồng):", ten_dau_chu)
print("Link Facebook:", link_fb)
print(f"Total property images: {len(property_images)}")
print(f"Total Red Book images: {len(sodo_images)}")
for idx, url in enumerate(sodo_images):
    print(f"  Sơ đồ thửa đất {idx+1}: {url[:60]}...")
