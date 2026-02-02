/**
 * Province Coordinates Mapping
 * Auto-generated from 63tinh-quandao.geojson
 * Contains centroids of 65 Vietnam provinces and islands
 */

export const PROVINCE_COORDS = {
  "Đà Nẵng": [
    16.1155,
    108.0792
  ],
  "Đồng Nai": [
    10.9453,
    107.1845
  ],
  "Đồng Tháp": [
    10.568,
    105.5609
  ],
  "Đăk Nông": [
    12.1532,
    107.7738
  ],
  "Đắk Lắk": [
    12.7657,
    108.2455
  ],
  "Điện Biên": [
    21.7441,
    102.9307
  ],
  "An Giang": [
    10.5321,
    105.2768
  ],
  "Bà Rịa - Vũng Tàu": [
    10.3547,
    107.1391
  ],
  "Bình Định": [
    14.0656,
    109.0836
  ],
  "Bình Dương": [
    11.198,
    106.6232
  ],
  "Bình Phước": [
    11.7435,
    106.856
  ],
  "Bình Thuận": [
    11.0332,
    108.0951
  ],
  "Bạc Liêu": [
    9.33,
    105.5162
  ],
  "Bắc Giang": [
    21.3939,
    106.4008
  ],
  "Bắc Kạn": [
    22.2032,
    105.8261
  ],
  "Bắc Ninh": [
    21.088,
    106.0909
  ],
  "Bến Tre": [
    10.0263,
    106.6017
  ],
  "Cà Mau": [
    8.8974,
    105.0402
  ],
  "Cao Bằng": [
    22.7281,
    106.1764
  ],
  "Cần Thơ": [
    10.0896,
    105.5693
  ],
  "Gia Lai": [
    13.8683,
    108.2129
  ],
  "Hà Giang": [
    22.7369,
    105.0203
  ],
  "Hà Nội": [
    21.0266,
    105.7217
  ],
  "Hà Nam": [
    20.5074,
    105.976
  ],
  "Hà Tĩnh": [
    18.2757,
    105.802
  ],
  "Hồ Chí Minh city": [
    10.5916,
    106.832
  ],
  "Hòa Bình": [
    20.7224,
    105.3434
  ],
  "Hưng Yên": [
    20.8211,
    106.0976
  ],
  "Hải Dương": [
    20.9443,
    106.3737
  ],
  "Hải Phòng": [
    20.774,
    106.937
  ],
  "Hậu Giang": [
    9.7653,
    105.5647
  ],
  "Khánh Hòa": [
    12.3689,
    109.2349
  ],
  "Kiên Giang": [
    10.0056,
    104.5183
  ],
  "Kon Tum": [
    14.7324,
    107.9317
  ],
  "Lào Cai": [
    22.3155,
    104.1537
  ],
  "Lâm Đồng": [
    11.9248,
    108.0942
  ],
  "Lai Châu": [
    22.2845,
    103.1359
  ],
  "Lạng Sơn": [
    21.8039,
    106.5306
  ],
  "Long An": [
    10.6685,
    106.3809
  ],
  "Nam Định": [
    20.2631,
    106.2583
  ],
  "Nghệ An": [
    19.1885,
    105.1341
  ],
  "Ninh Bình": [
    20.2317,
    105.8723
  ],
  "Ninh Thuận": [
    11.6893,
    108.9602
  ],
  "Phú Thọ": [
    21.3188,
    105.1367
  ],
  "Phú Yên": [
    13.2895,
    109.1441
  ],
  "Quảng Bình": [
    17.5983,
    106.3955
  ],
  "Quảng Nam": [
    15.5582,
    108.0834
  ],
  "Quảng Ngãi": [
    14.9847,
    108.7021
  ],
  "Quảng Ninh": [
    21.0635,
    107.3749
  ],
  "Quảng Trị": [
    16.74,
    106.9827
  ],
  "Sóc Trăng": [
    9.4649,
    105.8993
  ],
  "Sơn La": [
    21.2417,
    103.9922
  ],
  "Tây Ninh": [
    11.4097,
    106.2043
  ],
  "Thái Bình": [
    20.4818,
    106.4816
  ],
  "Thái Nguyên": [
    21.6968,
    105.9106
  ],
  "Thừa Thiên - Huế": [
    16.3394,
    107.6868
  ],
  "Thanh Hóa": [
    20.0536,
    105.2546
  ],
  "Tiền Giang": [
    10.395,
    106.4546
  ],
  "Trà Vinh": [
    9.7679,
    106.3828
  ],
  "Tuyên Quang": [
    22.0936,
    105.2883
  ],
  "Vĩnh Long": [
    10.0758,
    106.0157
  ],
  "Vĩnh Phúc": [
    21.3665,
    105.59
  ],
  "Yên Bái": [
    21.8821,
    104.525
  ],
  "QĐ.Hoàng Sa": [
    16.6735,
    112.3032
  ],
  "QĐ.Trường Sa": [
    10.8193,
    114.572
  ]
}

/**
 * Get coordinates for a province name
 * @param {string} provinceName - Name of province (e.g., "Hà Nội")
 * @returns {[number, number]} [latitude, longitude] or Vietnam center if not found
 */
export function getProvinceCoords(provinceName) {
  // Try exact match first
  if (PROVINCE_COORDS[provinceName]) {
    return PROVINCE_COORDS[provinceName]
  }
  
  // Try case-insensitive match
  const normalizedName = provinceName.trim()
  for (const [key, value] of Object.entries(PROVINCE_COORDS)) {
    if (key.toLowerCase() === normalizedName.toLowerCase()) {
      return value
    }
  }
  
  // Default to Vietnam center
  console.warn(`Province "${provinceName}" not found, using Vietnam center`)
  return [14.0583, 108.2772]
}
