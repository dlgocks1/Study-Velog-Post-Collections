# Web 5주차 워크북

### 핵심 키워드

- addEventListener
- JavaScript의 함수

---

#### EventListener란?

[MDN 이벤트 종류](https://developer.mozilla.org/ko/docs/Web/Events)
[이벤트 종류 2](https://jenny-daru.tistory.com/17)
HTMl 내에서 이벤트를 관리하고 처리할 수 있게 하는 것

사용자가 실제 이벤트를 발생시켰을 때 그 이벤트에 대응하여 처리하는 것  =>  '이벤트 핸들러'
'**이벤트 핸들러**'는 앞에 'on'을 붙여 주고 이벤트에 대한 동작(함수)을 처리 

```
//돔으로 선택한 변수들을 구별하기위해 $작성 -> 우리들의 약속
const $div = document.querySelector('.container');
const $form = document.querySelector('form');
const $input = document.querySelector('input');
const $button = document.querySelector('button');
querySelector #, ., 태그 등으로 선택
```

이벤트를 추가하는 방법 2가지
* 1. 이벤트 핸들러

```
 콜백 함수는 중첩 불가능
$div.onclick = handleClick;
 Arrow function
 $div.onclick = () => alert('container Clicked');
 function handleClick(){
     console.log('container Clicked');
 }
```

*  2. addEventLsitener

```
// 이벤트 리스너는 리스너를 다는것이여서 중첩가능
$div.addEventListener('click',()=>console.log('clicked'));
$div.addEventListener('click',handleClick);
$div.addEventListener('click',()=>alert('clicked'));

 function handleClick(){
     console.log("clicekd");
 }
 
 //removeEventListener로 이벤트삭제가능
 $div.removeEventListener('click',handleClick)


```

---

```
$div.addEventListener('click',handleClick);

//첫번째 매개변수는 무슨 이벤트인지 알려줌
function handleClick(e){
    console.log(e);
    console.log(e.target.innerText);
}
```

콘솔에 찍히는 e에 관한 수많은 정보들
![](https://velog.velcdn.com/images/cksgodl/post/d66a1ddc-a6ce-49fc-aeb9-1e956cb8924a/image.png)

target을 선택하면 div.container을 선택할 수 있다.

---

```
$input.addEventListener('change',handleChange);

function handleChange(e){
    console.dir(e.target);
    console.log(e.target.value);
}

```


여기서 알고가는 console.dir 과 console.log의 차이점
[객채의 데이터를 보고 싶을 때](https://sondho.tistory.com/50)

console.dir(객체)로 데이터를 확인 후, 사용하고 싶은 변수는 구글링해서 적용한다.
ex) JS innterHTml, window.innerWidth

* console.log()
	HTML과 유사한 트리에서 요소를 보여준다.
    
* console.dir()
	JSON과 같은 트리에서 요소를 보여준다.

---

[Event.preventDefault란?](https://developer.mozilla.org/ko/docs/Web/API/Event/preventDefault)

> Event 인터페이스의 preventDefault() 메서드는 어떤 이벤트를 명시적으로 처리하지 않은 경우, 해당 이벤트에 대한 기본 동작을 실행하지 않도록 지정합니다.

```
//form의 경우 엔터나 서브밋을 클릭하면 새로고침됨
$form.addEventListener('submit',handleSubmit);
function handleSubmit(e){
    //submit이벤트의 새로고침 막기
    e.preventDefault();
    const inputValue = $input.value;
    console.log(inputValue);
    $input.value = '';
}   
```

![](https://velog.velcdn.com/images/cksgodl/post/9e339926-4771-4b30-96ab-3a5ec927c7d1/image.png)

Hello를 Input에 넣고 submit 이벤트를 발생시키면 Hello가 콘솔에 출력된다.


### **실습 체크리스트✅**

Q.  왜 $div.onClick와 같은 방식 대신 addEventListener를 사용하시는지 이해하셨나요?
A.	onClick과 같은 Callback함수는 하나밖에 적용이 안되는데 반해 EventListener은 여러개 달수 있고, 관리도 편하다.


Q. preventDefault()를 사용하는 이유가 무엇인지 이해하셨나요?
A. 어떠한 이벤트에 기본 동작을 실행하지 않도록 지정할 수 있다.

**Q. addEventListener를 통해 핸들러 함수를 실행할 때, 파라미터를 넣어주려면 어떻게 해야하는지 조사하고 하단에 코드를 적어주세요.**
A. Handler 함수에 파라미터를 넣으면 -> Event 객체를 사용할 수가 없다. 그래서 event라는 파라미터를 따로 넣어주고 그다음 사용자의 변수를 적용한다.

[CallBack함수에 파라미터 남기기](https://23life.tistory.com/158)
![](https://velog.velcdn.com/images/cksgodl/post/677221e9-bcd5-4efe-8b70-c768437013ed/image.png)


```
$form.addEventListener('submit',(event)=>handleSubmit(event,$input.value));
function handleSubmit(e,inputValue){
    e.preventDefault();
    console.log(inputValue);
    $input.value = '';
}   
```


### 논의해보면 좋은 것들 🔥
- addEventListener에 필요한 인자들에 대해 알아보기
- JavaScript 이벤트의 종류에 대해 조사하기


### 실습 너튜브 클론
댓글을 form 과 input 및 submit 이벤트를 사용해 구현하였다.

```
const $commentList = document.querySelector("#commentsList");
const $commentForm = document.querySelector("#placeholder-area");
const $commentInput = document.querySelector("#commentInput");

$commentForm.addEventListener("submit",handleSubmit);
function handleSubmit(e){
    e.preventDefault();
    const newComment = $commentInput.value;

    // if (newComment !=""){
    if (!newComment){
        return;
    }
    const newCommentItem = commentItemTemplate("이해찬",newComment,"https://yt3.ggpht.com/yti/APfAmoFjoi5B8bE0j5805xHwq1nnfHaRErC54Tcwrre3=s88-c-k-c0x00ffffff-no-rj-mo");
    $commentList.insertAdjacentHTML("afterbegin",newCommentItem);
    $commentInput.value = "";
}


```

* commentItemTemplate 객체

```
const commentItemTemplate = (newId, newComment,Imgurl) => {
	return `
    <li class="commentItem">
    <img src="${Imgurl}"
        class="profileImg" />
    <div>
        <p id="commentName">${newId} <span id="commentLasttime"> 29초전</span></p>
        <p class="comment">${newComment}</p>
        <div class="flex commentreview-holder">
            <button class="commentBtn">
                <span class="commentIcon">
                    <svg viewBox="0 0 16 16" preserveAspectRatio="xMidYMid meet"
                        focusable="false" class="style-scope yt-icon"
                        style="pointer-events: none; display: block; width: 100%; height: 100%;">
                        <g class="style-scope yt-icon">
                            <path
                                d="M12.42,14A1.54,1.54,0,0,0,14,12.87l1-4.24C15.12,7.76,15,7,14,7H10l1.48-3.54A1.17,1.17,0,0,0,10.24,2a1.49,1.49,0,0,0-1.08.46L5,7H1v7ZM9.89,3.14A.48.48,0,0,1,10.24,3a.29.29,0,0,1,.23.09S9,6.61,9,6.61L8.46,8H14c0,.08-1,4.65-1,4.65a.58.58,0,0,1-.58.35H6V7.39ZM2,8H5v5H2Z"
                                class="style-scope yt-icon"></path>
                        </g>
                    </svg>
                </span>
            </button>
            <span class="reviewcnt"> 15</span>
            <button class="commentBtn">
                <span class="commentIcon">
                    <svg viewBox="0 0 16 16" preserveAspectRatio="xMidYMid meet"
                        focusable="false" class="style-scope yt-icon"
                        style="pointer-events: none; display: block; width: 100%; height: 100%;">
                        <g class="style-scope yt-icon">
                            <path
                                d="M3.54,2A1.55,1.55,0,0,0,2,3.13L1,7.37C.83,8.24,1,9,2,9H6L4.52,12.54A1.17,1.17,0,0,0,5.71,14a1.49,1.49,0,0,0,1.09-.46L11,9h4V2ZM6.07,12.86a.51.51,0,0,1-.36.14.28.28,0,0,1-.22-.09l0-.05L6.92,9.39,7.5,8H2a1.5,1.5,0,0,1,0-.41L3,3.35A.58.58,0,0,1,3.54,3H10V8.61ZM14,8H11l0-5h3Z"
                                class="style-scope yt-icon"></path>
                        </g>
                    </svg>
                </span>
            </button>
            <span class="reviewcnt"> 1</span>
            <button class="commentBtn" id="reviewBtn">
                답글
            </button>
        </div>
    </div>
</li>`
;
}
```


![](https://velog.velcdn.com/images/cksgodl/post/2cf7019c-eaab-4c72-b678-e09873885167/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/218cc1ec-79f8-4256-b44e-b8a15eb2b04a/image.png)

개념 
버블링, 캡쳐링

더 알아볼 것 
유투브 더보기, 플레이스트 2줄 ... 표시
