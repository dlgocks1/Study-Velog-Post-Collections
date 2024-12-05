## HTTP란??
>HTTP = HyperText Transfer Protocol

서버와 프론트간의 통신방법 중 하나

>HTTPS = HyperText Transfer Protocol Secure

HTTP에 보안을 더한 것

HTTP 데이터 통신의 특징은 Request와 Response로 이루어져 있다.

### HTTP Request Method
* GET : 정보를 가져올 떼
* POST : 정보를 추가할 때
* PUT : 정보를 수정할 때
* DELETE : 정보를 삭제할 때

똑같은 url로 정보를 요청해도 Method에 따라 활동이 달라진다.
[jsonplaceholder로 http request 해보기](https://jsonplaceholder.typicode.com/)

POST나 PUT메소드를 사용할 때는 header와 body에 데이터의 정보를 넣어줘야한다.

![](https://velog.velcdn.com/images/cksgodl/post/2abd7b5d-9433-4f1d-95ab-5851c63ae58f/image.png)


### HTTP Response

Response로 오는 데이터의 형식으로는 대표적으로 XML과 Json이 있다고 생각하면 될것 같다.
[XML과 JSON 파싱 안드로이드에서 사용해보기](https://velog.io/@cksgodl/%EA%B3%B5%EA%B3%B5%EB%8D%B0%EC%9D%B4%ED%84%B0-XML-%ED%8C%8C%EC%8B%B1-%EB%B0%8F-%ED%81%AC%EB%A1%A4%EB%A7%81%EC%9C%BC%EB%A1%9C-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EA%B0%80%EC%A0%B8%EC%98%A4%EA%B8%B0)

_JSON을 더 많이 사용함_

HTTP


## JS에서 브라우저와 통신하기

### fetch로 http Request요청하기

```
// 데이터 통신은 비동기로 이루어짐
// 1. fetch : fetch(url, options)

const result = [];

fetch("https://jsonplaceholder.typicode.com/users")
// 받아온 값은 Promise형태이기 때문에 JSON으로 변환
.then(res => res.json())
.then(data => {
    data.map(item =>
        // 이름만 가져올려면
        item.nameresult.push(item) 
        )})
.catch(error => console.log(error))

console.log(result);

```

출력 값
![](https://velog.velcdn.com/images/cksgodl/post/667482bd-5695-407a-a213-6411ad661c1b/image.png)

```
// 파라미터로 method, header, body를 넣을 수 있다.
fetch("URL", {
  method: "POST",
  mode: 'cors',
  cache: 'no-cache',
  headers:  {"Content-Type", "application/json"},
  credentials: "same-origin",
  body: JSON.stringify(bodyData)
});
```


#### await, async와 함께 사용하기

```
const datafetch = async() =>{
    const res = await fetch("https://jsonplaceholder.typicode.com/users");
    const data = await res.json();
    return data
}

const dataResult = datafetch();
// Promise객체가 반환됨
console.log(dataResult);

// then으로 후처리 하기
dataResult.then(
    it => console.log(it)
)
```

### axios사용해 받아오기

HTML내에 추가 axios lib추가

>```
<script src="https://unpkg.com/axios/dist/axios.min.js"></script> 
```

```
const result = [];

axios.get("https://jsonplaceholder.typicode.com/users")
.then(data => console.log(data.data))
```
axios는 결과값을 JSON으로 변환해줌
![](https://velog.velcdn.com/images/cksgodl/post/ffa53313-8da6-42ac-a564-94f1f0eebc68/image.png)

```
const datafetch = async() =>{
    const res = await axios.get("https://jsonplaceholder.typicode.com/users");
    // Promise 객체가 리턴됨
    return res;
}

const dataResult = datafetch();

// Promise임으로 then으로 사후처리
dataResult.then(
    data => console.log(data)
)
```

#### api를 호출하는 다른 라이브러리

[axios](https://www.npmjs.com/package/axios)
[bent](https://www.npmjs.com/package/bent)
node-fetch-npm
[request](https://www.npmjs.com/package/request)
superagent
[성능 비교 글](https://grepper.tistory.com/28)

다른 라이브러리도 비슷한 것 같아서 후에  React에서 많이 사용한다는 axios 위주로 사용해보면 좋을 것 같다.

---

## 실습


임의로 하드코딩 된 동영상 리스트를 Youtube API를 사용해 업데이트 해보기.
![](https://velog.velcdn.com/images/cksgodl/post/0aaaeae9-d20c-4299-a36a-ef2cd57fb035/image.png)


#### 유튜브 디자인 클론 코딩

>**HTML 구조**

```
<body>
  <totalContainer>
	<navContainer>
  		검색창, 알림창, 유투브 로고 
    </navContainer>
	<main>
    	<aside>
      		좌측 Icon Navigation, position : fixed
        </aside>
      	<mainContainer>
        	  <tagContainer>
          	   	액션, 요리, 음악등 태그 들
              </tagContainer>
          	  <mainContentBox>
              	메인화면 Content영상 박스  
          	  </mainContentBox>
      	</mainContainer>
    </main>
  </totalConatainer>
</body>
```
![](https://velog.velcdn.com/images/cksgodl/post/9d5a3453-db99-41e8-850f-76bde036a761/image.png)

vedioItemContainer 구조
```
<div class="vedioItemContainer">
    <a href="/">
        <img class="thumbnailImg" src="https://i.ytimg.com/vi/r_ALdsMbwqI/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAjjru2TcbeYVduYUJ3_ZxtCck1MA">
    </a>
  
    <div class="vedioDetailContainer">
        <a class ="videoChannelImgContainer" href="/">
            <img class="channelImg" src="https://yt3.ggpht.com/ytc/AKedOLSbkohOdcipSnw_pznXOl0se0rLnTdYKSVcz9BnKQ=s68-c-k-c0x00ffffff-no-rj">
        </a> 
        <a href="/">
            <div class="vedioMetaDetail">
                <div class="vedioTitle">
                    [MV] BOL4(볼빨간사춘기) - Seoul                                   
                </div>
                <div class="vedioMetaData">
                    <p>
                        SUPER SOUND Bugs!
                    </p>
                    <p>
                        <span> 조회수 74만회</span>
                        <span id="dot"></span>
                        <span>2주 전</span>
                    </p>
                </div>
            </div>
        </a>
    </div>
```

![](https://velog.velcdn.com/images/cksgodl/post/3fd009a5-1742-4ca9-8c72-4f5b58e16808/image.png)

aside 구조

  ```
<aside>
    <ul class="sideCategoryList">
        <li class="sideCategoryItem">
            <a href="/" class="sideCategoryContainer">
            <span class="sideCategoryIcon">
                <svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" class="style-scope yt-icon" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g class="style-scope yt-icon"><path d="M4,10V21h6V15h4v6h6V10L12,3Z" class="style-scope yt-icon"></path></g></svg>
            </span>
            <span class="sideCategoryTitle">
            홈
            </span>
    </a>
    </li>
      ...
  	</ul>
  </aside>
      
```
ul과 li로 리스트 관리
  ![](https://velog.velcdn.com/images/cksgodl/post/360ea826-9461-4af5-88f6-0420f71e2219/image.png)

  ---

  
  [유투브 API](https://developers.google.com/youtube/v3/docs/videos/list?apix=true&apix_params=%7B%22part%22%3A%5B%22snippet%2C%20statistics%22%5D%2C%22chart%22%3A%22mostPopular%22%2C%22maxResults%22%3A1000%2C%22regionCode%22%3A%22KR%22%7D)에서 동영상 가져오는 HTTP 명세서 확인

[구글 클라우드 플랫폼](https://console.cloud.google.com/apis/credentials/key/db4d5c28-45ad-4916-a661-fd671af5fef1?project=youtube-clone-349704)에서 API키를 생성
  
  
```
// In JS
const YOUR_API_KEY = "MY API KEY";
const $contentBox = document.querySelector('.contentBox')

function fetchVedio(){
  // axios를 사용하여 Http Request 전송 및 반환된 Promise객체 사후처리
  axios.get(`https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2C%20statistics&chart=mostPopular&maxResults=1000&regionCode=KR&key=${YOUR_API_KEY}`)
    .then(res => {
         res.data.items.map(item=>
			// vedio를 추가하는 함수
  			vedioCardTemplate(item))
    })
    .catch(error => console.log(error))
}

fetchVedio();
```
  
 
```
function vedioCardTemplate(data){
  	// vedioItem HTML 코드 템플릿
    const vedioItem = `
    <div class="vedioItemContainer">
    // data에서 받아온 정보들을 뿌려준다.
    <a href=${`https://www.youtube.com/watch?v=${data.id}`}>
        <img class="thumbnailImg" src=${data.snippet.thumbnails.medium.url}>
    </a>
    <div class="vedioDetailContainer">
        <a class ="videoChannelImgContainer" href=${`https://www.youtube.com/channel/${data.snippet.channelId}`}>
            <img class="channelImg" src="https://yt3.ggpht.com/ytc/AKedOLSbkohOdcipSnw_pznXOl0se0rLnTdYKSVcz9BnKQ=s68-c-k-c0x00ffffff-no-rj">
        </a> 
        <a href=${`https://www.youtube.com/watch?v=${data.id}`}>
            <div class="vedioMetaDetail">
                <div class="vedioTitle">
                    ${data.snippet.title}                                   
                </div>
                <div class="vedioMetaData">
                    <p>
                    ${data.snippet.channelTitle}    
                    </p>
                    <p>
                        <span> ${vedioViewTextControle(data.statistics.viewCount)}
                            </span><span id="dot"></span>
                            <span>${luxon.DateTime.fromISO(data.snippet.publishedAt).toRelative()}</span>
                    </p>
                </div>
            </div>
        </a>
    </div>
</div>`
    // contentBox에 아이템 추가   
    $contentBox.insertAdjacentHTML('beforeend',vedioItem);
}

// 조회수 : "21542546"를 Typed된 Text로 뿌려주는 함수
function vedioViewTextControle(view){
    if( Number(view) > 10000){
        return "조회수 : "+(Number(view)/10000).toFixed(0) + '만회';
    }else if(Number(view) > 100){
        return "조회수 : "+(Number(view)/100).toFixed(0) + '천회';
    }
    else{
        return "조회수 : "+(Number(view)).toFixed(0) + '회';
    }
    return view
}
```
  
유튜브 클론 최종 모습
  
  ![](https://velog.velcdn.com/images/cksgodl/post/c3b32e4a-90bd-401a-9130-1e3836238e00/image.png)
  
  디테일 페이지도 한번 바꿔봤다.
  ![](https://velog.velcdn.com/images/cksgodl/post/6b3b60ec-3cab-4a04-bd58-74025c000f56/image.png)


  [HaeChan_8Week 과정](https://github.com/KAU-UMC/web-study)