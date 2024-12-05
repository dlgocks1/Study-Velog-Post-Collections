### 컴포저블의 상태
Compose에서의 컴포넌트는 `remember` API를 사용하여 메모리에 객체를 저장할 수 있다.

왜? remember객체를 사용해야 하는가?

remember에 의해 계산된 값은 초기 컴포지션 중에 컴포지션에 저장되고 저장된 값은 리컴포지션 중에 반환된다. 

![](https://velog.velcdn.com/images/cksgodl/post/8984a742-56c8-4253-8cb3-9d5ef6ab41d6/image.png)

>
`초기 컴포지션`: 처음 컴포저블을 실행하여 컴포지션을 만드는 것
`컴포지션`: Jetpack Compose가 컴포저블을 실행할 때 슬릇 테이블에 초기 갭이 할당되고 최초 상태의 컴포저블 데이터가 등록되는 것
`리컴포지션`: 데이터가 변경될 때 컴포지션을 업데이트하기 위해 컴포저블을 다시 실행하는 것


```
interface MutableState<T> : State<T> {
    override var value: T
}
```
`mutableStateOf`객체를 활용하여 value가 변경되면 value를 읽는 구성 가능한 함수의 리컴포지션이 예약된다.

이러한 State를 위임받은 객체는 이 value 값을 사용하는 함수들에게 자동으로 Observing된다.

예시
```
val mutableState = remember { mutableStateOf(default) }
var value by remember { mutableStateOf(default) }
val (value, setValue) = remember { mutableStateOf(default) }
```
여기서 by를 사용한 위임을 사용하기 위해서는 다음을 import해야한다.
```
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
```

### 꼭 State, MutableState만을 써야하나요??

라고 말하면 그렇다, 꼭 써야한다. 왜냐하면 Jetpack Compose에서는 상태가 변할 때만 Jetpack Compose가 자동으로 재구성되기 때문이다.

기존에 안드로이드에서 사용하던 Observable 데이터 형식들
* LiveData
* Flow
* RxJava2

를 사용하기 위해서는 `State<T>`로 변환하여 사용해야 한다. 
Compose에는 Android 앱에 사용되는 관찰 가능한 객체로 부터 `State<T>`를 만들 수 있는 함수가 내장되어 있다.

#### 정리
>요점 : Compose는 `State<T>` 객체를 읽어오면서 자동으로 재구성된다.
Compose에서 LiveData 같은 Observable한 또 다른 유형을 사용할 경우 컴포저블에서 LiveData<T>.observeAsState() 같은 구성 가능한 확장 함수를 사용하여 `State<T>`로 변환해야 한다.
  
추가적으로 Compose에서 `State`에 `ArrayList<T>` 또는 `mutableListOf()`와 같이 변경가능한 객체를 사용하면 안된다. `get()`을 이용해 프로퍼티가 바뀌어야만 리컴포지션이 트리거 되기 때문에 listOf()와 같은 변경 불가능한 객체를 사용하던가, 데이터 홀더를 사용하자.
  
#### 스테이트풀(Stateful)과 스테이트리스(Stateless)

 remember를 사용하여 객체를 저장하는 컴포저블은 내부 상태를 생성하여 컴포저블을 스테이트풀(Stateful)로 만든다.
  
 내부에 상태를 갖는 컴포저블은 재사용 가능성이 적고 테스트하기 어렵다. 외부에서 상태를 선언하고 컴포저블을 `Stateless`하게 유지하자.
  
**스테이트리스(Stateless)** 컴포저블은 상태를 갖지 않는 컴포저블이다. 스테이트리스(Stateless)를 달성하는 한 가지 쉬운 방법은 상태 호이스팅을 사용하는 것이다.  

  #### 상태 호이스팅
  Compose에서 상태 끌어올리기는 컴포저블을 스테이트리스(Stateless)로 만들기 위해 상태를 컴포저블의 호출자로 옮기는 패턴이다. 
  
  상태 및 상태를 변경가능한 함수를 콜백함수로 끌어 올려서 부모쪽에서 상태를 관리하며 자식은 Stateless상태로 만드는 것을 의미한다.
  
  
  
```
@Composable
fun HelloScreen() {
    var name by rememberSaveable { mutableStateOf("") }

    HelloContent(name = name, onNameChange = { name = it })
}

@Composable
fun HelloContent(name: String, onNameChange: (String) -> Unit) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text(
            text = "Hello, $name",
            modifier = Modifier.padding(bottom = 8.dp),
            style = MaterialTheme.typography.h5
        )
        OutlinedTextField(
            value = name,
            onValueChange = onNameChange,
            label = { Text("Name") }
        )
    }
}
```
  * value: T: 표시할 현재 값
* onValueChange: (T) -> Unit: T가 제안된 새 값인 경우 값을 변경하도록 요청하는 이벤트

  ![](https://velog.velcdn.com/images/cksgodl/post/a0be1aaa-f9b8-4cfe-8b44-3f0cd6432228/image.png)
이렇게 상태를 끌어올리면 더 쉽게 컴포저블을 관리하고 재사용하며 테스트할 수 있다.
  이렇게 상태가 내려가고 이벤트가 올라가는 패턴을 단방향 데이터 흐름이라고 한다. 
  **UI의 상태를 표시하는 컴포저블과 상태를 저장하고 변경하는 부분을 서로 분리할 수 있다.**
  
  ### 상태 호이스팅의 장점
  * **단일 소스 저장소**: 여러 컴포저블에서 사용하는 상태를 단일로 저장한다.
  * **캡슐화**: 스테이트풀(Stateful)한 부모만 상태를 수정 가능하다.
  * **공유 가능**: 끌어올린 상태를 여러 Composable과 공유 가능하다.
  * **가로채기 가능**: 스테이트리스(Stateless) 변경 함수는 상태를 변경하기 전에 이벤트를 무시할지 수정할지 결정할 수 있다.
  * **분리됨**: 스테이트리스(Stateless) 상태는 어디에나 저장할 수 있다.
  
  >핵심 사항: 상태를 끌어올릴 때 상태의 이동 위치를 쉽게 파악할 수 있는 세 가지 규칙이 있다.
  1. 상태는 적어도 그 상태를 사용하는 모든 컴포저블의 가장 낮은 공통 상위 요소로 끌어올려야 한다(읽기).
  2. 상태는 최소한 변경될 수 있는 가장 높은 수준으로 끌어올려야 한다(쓰기).
  3. 동일한 이벤트에 대한 응답으로 두 상태가 변경되는 경우 두 상태를 함께 끌어올려야 한다.
  
![](https://velog.velcdn.com/images/cksgodl/post/1299eae5-b421-484a-92b0-4d98ab1bc1b2/image.png)
상태를 너무 많이 끌어 올리면 상태를 사용하지 않는 컴포넌트가 `리컴포지션`될 수 있다. 상태를 사용하는 컴포넌트들의 최저 부모로 끌어 올리자.
  
## 상태 관리
  
 호이스팅을 이용해 함수 자체에서 관리 가능하지만, 그러나 추적할 상태의 양이 늘어나거나 구성 가능한 함수에서 실행할 로직이 발생하는 경우 로직과 상태 책임을 다른 클래스, 즉 `상태 홀더`에 위임하는 것이 좋다.
  
  상태홀더로써는 `ViewModel`을 사용할 수 있다.
  `뷰모델`은 비즈니스 로직 및 화면 상태나 UI 상태에 대한 정보를 제공한다.

  ```
  @HiltViewModel
class SearchViewModel @Inject constructor() : ViewModel() {
    private val _searchStrResult: MutableState<String> = mutableStateOf("")
    val searchStrResult: State<String> get() = _searchStrResult

    fun handleUpdateSearchResult(str: String) {
      _searchStrResult.value = str
    }
  }
  ```
  
  다음과 같이 뷰모델에서 `State<String>`를 관리하여 UI 상태에 대한 정보를 제공한다.
  
ViewModel의 생명주기는 Compose 콘텐츠의 호스트의 생명 주기나 탐색 그래프의 수명 주기를 따르기 때문에 ViewModel은 컴포지션보다 수명이 더 길다.
ViewModel은 수명이 길기 때문에 컴포지션의 수명에 바인딩된 상태에 관한 장기 지속 참조를 보유해서는 안 된다. 관련 장기 지속 참조를 보유하면 메모리 누수가 발생할 수 있다.
  
  화면 수준 컴포저블에서 ViewModel 인스턴스를 사용하여 비즈니스 로직 액세스 권한을 제공하고 UI 상태의 정보 소스가 되는 것이 좋다. **ViewModel 인스턴스를 다른 컴포저블에 전달해서는 안 된다.**
  
  즉 다음과 같은 소스는 사용하면 안된다.
  ```
  val searchViewModel = hiltViewModel<SearchViewModel>()
  
  ...
  
  composable(Screen.Bookmark.route) { BookmarkScreen(searchViewModel = searchViewModel) }
  composable(Screen.Mypage.route) { MypageScreen(searchViewModel = searchViewModel) }
  ```
  이렇게 ViewModel 인스턴스를 다른 컴포저블에 전달하여 사용해서는 안되며 액티비티내에서 공유해야할 무엇인가가 있다면
  
  1.  뷰 모델의 동일한 인스턴스를 가져오기 위해 이전 백 스택 항목을 전달할 수 있다.
  ```
  val navController = rememberNavController()
NavHost(
    navController = navController,
    ...
) { 
    composable("ScreenA") { backStackEntry ->
        val viewModel: MyViewModel = viewModel(backStackEntry)
        ScreenA(viewModel)
    }
    composable("ScreenB") { backStackEntry ->
        val viewModel: MyViewModel = viewModel(navController.previousBackStackEntry!!)
        ScreenB(viewModel)
    }
} 
  ```
  
  2. 싱글톤 객체를 선언하여 뷰모델에서 수정하자
  
  ```
  object SharedSignInObject {
    fun signUp(name: String) {
        // do something
    }
}

  // 뷰모델
class MyViewModel: ViewModel() {
    fun signUp(name: String) {
        SharedSignInObject.signUp(name)
    }
}
  ```
  
  [How can I share viewmodel from one screen to another screen in jetpack compose?](https://stackoverflow.com/questions/71904938/how-can-i-share-viewmodel-from-one-screen-to-another-screen-in-jetpack-compose)
  
  