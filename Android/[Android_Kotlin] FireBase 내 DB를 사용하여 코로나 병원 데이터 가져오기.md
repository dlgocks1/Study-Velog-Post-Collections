### Firebase 시작하기

[Firebase  홈페이지](https://firebase.google.com/?hl=ko&gclid=CjwKCAjw9LSSBhBsEiwAKtf0nx3j83jWx6WPbl9d1RK86wdKHqMeCH7Nya_EzlET0WTbz31LMUX15hoCPL8QAvD_BwE&gclsrc=aw.ds)
에서 프로젝트 생성 

* 페이지에서 시키는대로 진행 한다.

* 파이어 베이스 구성 파일(google-service.json)을 다운로드 하여 프로젝트 app폴더에 넣는다.

![](https://velog.velcdn.com/cloudflare/cksgodl/ed71bcb0-e48b-46a9-80d6-dc8f99525992/image.png)

* signingReport에서 SHA1 찾아서 키값 입력
signingReport 없으면 file - setting 에서 
do not build Gradle task list during Gradle sync 체크 해제
rebuild project
![](https://velog.velcdn.com/cloudflare/cksgodl/449a6eca-0dc5-494f-95a2-90da35daa70f/image.png)


* Module 단의 Gradle에서 firebase 추가

```
//firebase
    implementation platform('com.google.firebase:firebase-bom:29.2.1')
    implementation 'com.google.firebase:firebase-analytics-ktx'
```


* 간단한 DB사용 예제임으로 read write 권한을 모두 true로 설정
( 모든 유저가 DB를 수정할 수 있음으로 위험)
![](https://velog.velcdn.com/cloudflare/cksgodl/1736c56f-af81-4346-8513-f69498112b47/image.png)

실시간 데이터베이스에서 JSON을 사용하여 데이터를 내보내거나 가져올 수 있다.

![](https://velog.velcdn.com/cloudflare/cksgodl/d6214cce-aca3-419f-bd71-b385ad32c859/image.png)

[공공 데이터 포탈 (코로나19병원정보) ](https://www.data.go.kr/iim/api/selectAPIAcountView.do)
공공 데이터 포털에서 코로나 19병원정보를 활용신청하여 DB에 넣었다.

![](https://velog.velcdn.com/cloudflare/cksgodl/1fe377f3-22b8-4663-b08e-9272dc933be4/image.png)

response -> body -> items -> item 에 각각 병원의 정보가 들어가 있다.

**이러면 사용준비 완료**

퍼미션 관리
```
 <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    <uses-permission android:name="android.permission.INTERNET" />

```

네이버 지도 쓰는 법은 나중에
```
<meta-data
            android:name="com.naver.maps.map.CLIENT_ID"
            android:value="ID" />
         
```


**코드내에서 파이어베이스 객체 접근**
```
//파이어베이스 접근하기 위한 객체 생성
private lateinit var database: DatabaseReference
```


```
//OnCreate에서 database 객체를 초기화 해줬다.
database = FirebaseDatabase.getInstance().reference
```

response -> body -> totalCount 를 들고와서 totalCount값만큼 리스트에 추가하기

```
//토탈카운트 들고오기
database.child("response").child("body").child("totalCount").get().addOnSuccessListener {
            totalcount = Integer.parseInt(it.value as String)
            SetHospitalDatabase()
        }.addOnFailureListener{
        }
        
```
response -> body -> items -> item 의 값들을 totalcount의 숫자만큼 for문을 돌면서 데이터를 가져오기 
(리스트 채로 가져오는 더 좋은 방법이 있을 듯)


```
private fun SetHospitalDatabase() {
        hospitaldata = ArrayList<Hospitaldata>()
        //경우에 따라 서버의 업데이트된 값을 확인하는 대신 로컬 캐시의 값을 즉시 반환하고 싶을 수 있습니다.
        // 이 경우에는 addListenerForSingleValueEvent을 사용하여 로컬 디스크 캐시에서 데이터를 즉시 가져올 수 있습니다.
        database.child("response").child("body").child("items").child("item").addListenerForSingleValueEvent(object:
            ValueEventListener {
            override fun onDataChange(it: DataSnapshot) {
                for (i in 0 until totalcount) {
                    hospitaldata.add(
                        Hospitaldata(
                            Integer.parseInt(it.child(i.toString()).child("rnum").value.toString()),
                            it.child(i.toString()).child("ratPsblYn").value.toString(),
                            it.child(i.toString()).child("XPosWgs84").value.toString(),
                            it.child(i.toString()).child("telno").value.toString(),
                            it.child(i.toString()).child("YPosWgs84").value.toString(),
                            it.child(i.toString()).child("pcrPsblYn").value.toString(),
                            it.child(i.toString()).child("yadmNm").value.toString(),
                            it.child(i.toString()).child("YPos").value.toString(),
                            it.child(i.toString()).child("rprtWorpClicFndtTgtYn").value.toString(),
                            it.child(i.toString()).child("recuClCd").value.toString(),
                            it.child(i.toString()).child("XPos").value.toString(),
                            it.child(i.toString()).child("sidoCdNm").value.toString(),
                            it.child(i.toString()).child("addr").value.toString(),
                            it.child(i.toString()).child("mgtStaDd").value.toString(),
                            it.child(i.toString()).child("sgguCdNm").value.toString(),
                            it.child(i.toString()).child("ykihoEnc").value.toString(),
                        )
                    )
                }
//                1) 위도만 0.01바꾸었을 경우 거리  1110m 정도 바뀜 latitude 위도
//                2) 경도만 0.01바꾸었을 경우 거리  890m 정도 바뀜
                for (i in hospitaldata){
                    if(i.YPosWgs84 == "null" || i.XPosWgs84 == "null"){
                        continue
                    }
                    if( latitude-0.05 <= i.YPosWgs84!!.toDouble()  && i.YPosWgs84!!.toDouble() <= latitude+0.05 &&
                        longitude-0.05 <= i.XPosWgs84!!.toDouble() && i.XPosWgs84!!.toDouble() <= longitude+0.05){
                        setMarker(i.YPosWgs84!!.toDouble(),i.XPosWgs84!!.toDouble(),i.yadmNm,i.addr,i.ratPsblYn,i.pcrPsblYn)
                    }
                }
                naverMap.setOnMapClickListener { pointF: PointF, latLng: LatLng ->
                    for (i in infoWindowlist){
                        i.close()
                    }
                }
            }
            override fun onCancelled(error: DatabaseError) {
                Log.e("test", "Error getting data"+error.toString())
            }
        })
```

사용자의 경위도를 비교하여 약 5km 내의 모든 병원의 네이버지도에 마커를 찍어줬다.

```
if( latitude-0.05 <= i.YPosWgs84!!.toDouble()  && i.YPosWgs84!!.toDouble() <= latitude+0.05 &&
                        longitude-0.05 <= i.XPosWgs84!!.toDouble() && i.XPosWgs84!!.toDouble() <= longitude+0.05){
                        setMarker(i.YPosWgs84!!.toDouble(),i.XPosWgs84!!.toDouble(),i.yadmNm,i.addr,i.ratPsblYn,i.pcrPsblYn)
                    }
```


** +) 사용자의 위치 가져오는 함수
**
```
fun getLastKnownLocation() {
//permission Check
        if (ActivityCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.ACCESS_COARSE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            return
        }
        fusedLocationClient.lastLocation
            .addOnSuccessListener { location->
                if (location != null) {
                    latitude = location.latitude
                    longitude = location.longitude
                    Log.d("현재 사용자 좌표 : getLastKnownLoaction",latitude.toString()+longitude.toString())
                }
            }
    }
```

![](https://velog.velcdn.com/cloudflare/cksgodl/b1c1c82f-bf1d-4639-a106-8538b4978752/image.png)

근처 코로나 신속항원검사, PCR검사 가능한 병원들을 출력해 준다.

![](https://velog.velcdn.com/cloudflare/cksgodl/be806449-f874-4d4f-976f-969dccd09908/image.png)

공공데이터 포탈에 있는 데이터를 좀 더 다듬으면 마커마다 신속항원검사가 가능한지, PCR만 가능한지, 전화번호 등을 출력해 줄 수 있을 것이다.

---
구글 플레이스토어가 코로나19 유행과 같은 비극적인 사건에서 이익을 얻는 것을 규제하겠다는 이유로 코로나 관련 앱 검색을 제한하는 조치를 시행하여
Play Store에 등록은 안된다.