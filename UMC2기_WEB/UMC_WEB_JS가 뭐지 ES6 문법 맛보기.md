### 핵심 키워드

- JavaScript
    - ES6
- JavaScript 문법
    - 선언, 변수, 조건문, 반복문, 함수, 배열
    
### ECMAScript6란?
 
![](https://velog.velcdn.com/cloudflare/cksgodl/13b12e9f-88b5-4a7e-8011-4b28cad377e8/image.png)

ES란, ECMAScript의 약자이며 자바스크립트의 표준, 규격을 나타내는 용어이다.

새로운 언어 기능이 포함된 주요 업데이트

**업데이트 리스트**

* ** const and let**
	- const는 변경되지 않으며 재할당 불가. 새로운 값을 제공하려고 하면 오류가 반환됩니다.
	- let은 새로운 값을 가질 수도 있고 재할당 가능

* ** Arrow functions(화살표 함수)**
	만약 함수의 본문(body)에 return만 있는 경우 화살표 함수는 return과 {}를 생략할 수 있다. 단, 같이 생략해야한다.
return문에서 소괄호는 사용가능하다.
```
// 함수 표현식 - 화살표 함수 (생략형)
const plusFn = (a, b) => a + b;
```

* ** Template Literals(템플릿 리터럴)**
문자열을 연결하기 위해 더하기(+) 연산자를 사용할 필요는 없으며, 백틱(`)을 사용하여 문자열 내에서 변수를 사용할 수도 있습니다.
```
let str3 = `Hello ${str1} ${str2}`;
```

* ** Default parameters(기본 매개 변수)**
기존에는 함수의 매개변수에 초기화를 하려면 내부 작업이 필요했으나, ES6 에서는 필요 없어졌다.
```
const myFunc = (name, age = 22) => {
	return `안녕 ${name} 너의 나이는 ${age}살 이니?`; 
};

console.log(myFunc1('영희'));
// 출력 => 안녕 영희 너의 나이는 22살 이니?
```

* ** Array and object destructing(배열 및 객체 비구조화) **
	비구조화를 통해 배열 또는 객체의 값을 새 변수에 더 쉽게 할당할 수 있습니다.
	+) 속성 이름과 동일하지 않은 변수를 할당하면 undefined가 반환됩니다.
```
const contacts = {
	famillyName: '이',
	name: '영희',
	age: 22
};
// ES5 문법
let famillyName = contacts.famillyName;
let name = contacts.name;
let myAge = contacts.age;

// ES6 문법
let { famillyName, name, age } = contacts;

```

* ** Import and export(가져오기 및 내보내기) **
export를 사용하면 다른 JavaScript 구성 요소에 사용할 모듈을 내보낼 수 있습니다. 우리는 그 모듈을 우리의 컴포넌트에 사용하기 위해 가져오기 import를 사용합니다.
```

// ./detailComponent In ES6 
export default function detail(name, age) {
	return `안녕 ${name}, 너의 나이는 ${age}살 이다!`;
}

// Other File
import detail from './detailComponent';
console.log(detail('영희', 20));
// 출력 => 안녕 영희, 너의 나이는 20살 이다!
```

* **Promises(프로미스)**
	- Promise는 ES6의 새로운 특징이자 비동기 코드를 쓰는 방법입니다. 
    예를 들어 API에서 데이터를 가져오거나 실행하는데 시간이 걸리는 함수를 가지고 있을 때 사용할 수 있습니다. Promise는 문제를 더 쉽게 해결할 수 있다. 
    콜백함수 생각하면 될 듯?
```
const myPromise = () => {
//resolve및 reject로 예상 오류를 처리 할 수 있습니다.
	return new Promise((resolve, reject) => {
		resolve('안녕하세요 Promise가 성공적으로 실행했습니다');
	});
};

cosole.log(myPromise());
// Promise {<resolved>: "안녕하세요 Promise가 성공적으로 실행했습니다"}
```   


* ** Rest parameter and Spread operator(나머지 매개 변수 및 확산 연산자) **
	Rest parameter는 배열의 인수를 가져오고 새 배열을 반환하는데 사용됩니다.
또한 Rest parameter는 Array로 반환된다.
```
function fun1(...theArgs) {
    console.log(theArgs.length);
}

fun1();  // 0
fun1(5); // 1
fun1(5, 6, 7); // 3

//출처: https://beomy.tistory.com/16 [beomy]

```
![](https://velog.velcdn.com/cloudflare/cksgodl/7a61e39e-dcd0-46aa-ae5b-9c6bcf47af70/image.png)
![](https://velog.velcdn.com/cloudflare/cksgodl/1f9d8d5a-a3a7-4fd4-a0a4-c17a00bb2933/image.png)

```
const arr = ['영희', 20, '열성적인 자바스크립트', '안녕', '지수', '어떻게 지내니?'];

const Func = (...anArray) => {
	return anArray;
};

console.log(Func(arr));
// 출력 => ["영희", 20, "열성적인 자바스크립트", "안녕", "지수", "어떻게 지내니?"]
```
* ** Classes(클래스)**
 우리가 아는 그 클래스
```
class myClass {
	constructor(name, age) {
		this.name = name;
		this.age = age;
	}

	sayHello() {
		console.log(`안녕 ${this.name} 너의 나이는 ${this.age}살이다`);
	}
}

// myClass 메서드 및 속성 상속
class UserProfile extends myClass {
	userName() {
		console.log(this.name);
	}
}

const profile = new UserProfile('영희', 22);

profile.sayHello(); // 안녕 영희 너의 나이는 22살이다.
profile.userName(); // 영희
```

    


---

### JavaScript 문법

- 변수
    - [ ]  const : 데이터 값이 변하지 않을 때
    - [ ]  let : 데이터 값이 변할 수 있음
 
```
const = val
let = var
```
* 자료형
    - [ ]  string : 문자열
    - [ ]  boolean : True, False
    - [ ]  undefined : 자동적으로 값이 없음
    - [ ]  null : 수정적으로 비어있는 값
    - [ ]  bigInt : 큰값의 숫자
    - [ ]  symbol : 중복되지 않는 고유값
    - [ ]  obejct : 함수 배열 객체 등을 의미
    

* 산술연산자, 논리연산자..
	+ - = ==, !==, !=, &&, ||, ! .....
    
- 배열
    - [ ]  push : 배열 뒤에 추가
    - [ ]  unshift : 배열 앞에 추가
    - [ ]  splice : 원하는 곳에 추가 및 삭제
    splice(시작 index, 삭제하고 싶은 원소의 개수, 추가하고 싶은 원소들)
    - [ ]  pop : 배열 뒤에 삭제
    - [ ]  shift : 배열 앞에 삭제
    
```
//선언
const travel_spot = new Array("1","2","3");
const travel_spot = [];
const travel_spot = new Array();

//접근
travel_spot[0];

//추가 및 삭제
travel_spot.push("4");
travel_spot.unshift("5");
travel_spot.splice(2,0,"6","7"); //2번째 인덱스에서 0개의 원소를 지우고 6 ,7 추가
travel_spot.pop();
travel_spot.shift();


```
   
---

- 객체
    - [ ]  배열과 객체의 차이 : 키, 밸류값으로 접근, 함수도 객체 내에 지정 가능
    - [ ]  생성자 함수 : blue print, 생성자 함수
    
```
//const pooh = ['pooh','bear','disney character', 'boy'];
const pooh = {
  name : 'pooh',
  species : 'bear',
  job : 'disney character',
  gender : 'boy',
  sayHi : function(){
    console.log("Say Hello");
  }
}

pooh['say-bye'] = function(){
  console.log("Say Bye");
}

//객체내 함수를 실행할 땐 ()붙이기
pooh.favorites = ['honey','friends','cake'];
console.log(pooh['say-bye']());

//객체 키값 삭제
delete pooh.favorites

//객체를 생성자로 만들기
function Character(name, species, job, gender){
  this.name = name;
  this.species = species;
  this.job = job;
  this.gender = gender;
  this['sayHi'] = function(){
    console.log('Say Hi2 Im ' + this.name);
  };
  this['say-bye'] = function(){
    console.log("Say Hi2 ${this.gender}");
  };
}

const winnie_the_pooh = new Character("winnie the pooh", 'bear', 'disney character', 'boy');

const snoopy = new Character("snoopy", 'dog', 'comic character', 'boy');

const pikachu = new Character("pikachu", 'squirrel', 'pokekmon character', 'boy');

//console.log(winnie_the_pooh['sayHi']());
console.log(pikachu['sayHi']());

```

---
    
- 함수
    - [ ]  function : 함수 선언
    - [ ]  arrow function : 여러가지 생략해서 함수선언 가능
    
```
//일반적인 함수 선언
function multiply10(num){
   return num*10;
 }

//arrow function은 여러가지를 생략해서 사용가능
//인자나 리턴값이 하나일 때 예시
const multiply10 = num => num*10;

const data = multiply10(1000);
console.log(data);

```
---
- 조건문
    - [ ]  **if문이 거짓으로 판단하는 값 **: 0, false
    - [ ]  **삼항연산자** : 조건 ? 참일때 실행될 코드 : 거짓일때 실행될 코드
    - [ ]  **if, else if, else문과 switch문의 차이** : if문은 값이 true가 되면 else if, else를 실행 X, Switch는 case 내로 들어가도 다음 case에도 또 들어감
    
```
let age = 15;

//조건문 
if (age > 19){
  console.log("술을 마실 수 있다.");
}
else{
  console.log("아직 이르다.");
}

// 삼항연산자 : 조건 ? 참일때 실행될 코드 : 거짓일때 실행될 코드
const result = age > 19 ? "술을 마실 수 있다." : "아직 이르다.";
console.log(result);

if (age < 10){
  console.log("유아");
}else if(age <20){
  console.log("10대");
}else if(age <30){
  console.log("20대");
}else{
  console.log("노인");
}

switch(age){
  case 70:
    console.log("70대");
    break;
  case 20:
    console.log("20대");
    break;
  default:
    console.log("응애");
}

```

---

- 반복문
    - [ ]  for문과 while문을 사용하여 아래 배열의 index값들을 각 10씩 더한 반복문을 작성해주세요.
    
```
    const numArr = [77, 81, 12, 34, 51, 20];

  	for (let i=0; i<numArr.length ; i++){
    	console.log("for : "+ (parseInt(numArr[i])+10));
  	}

  	let i = 0;
  	while (i< numArr.length){
    	console.log("while : "+ (parseInt(numArr[i])+10));
    	i++;
	}

```
    
```
//한번은 실행하고 싶으면 do while문
do{
  console.log(i);
  i++;
}while(i<11)

```
   
---

### 논의해보면 좋은 것들

- JavaScript를 이용한 서비스들에 대해 알아보세요! (Web, App, Blockchain etc)

1. 웹 Front-End 프로그래밍
2. React와 Vue 
3. Back-End (node.js)
4. App 내에서의 사용 React-native
5. DataBase (MongoDB, Realm)
6. PC Program
	 ![](https://velog.velcdn.com/cloudflare/cksgodl/5db7b6fc-d06d-4fe7-9030-bd7f17fb20c2/image.png)
     뱀파이어 서바이벌은 JavaScript로 만들어졌다.

    

- JavaScript의 장점과 단점
    - 더 알고 싶다면 TypeScript의 등장에 대해서 얘기 나눠보세요!
    
TypeScript가 무엇인지??