### [Best pratices for saving UI state on Android](https://www.youtube.com/watch?v=V-s4z7B_Gnc&list=PLWz5rJ2EKKc85Xna4Q3Fw79OP_3D1JaJW&index=25)
의 내용을 정리한 글입니다.

## Losing App State

디바이스 화전, 다크모드와 화이트모드 변환, 액티비티의 종류, 재생성 등의 행동으로 인해 앱의 상태는 삭제되게 됩니다. 이를 `Configuration Changes`라고 불리우며 해당 변화에 따라 앱은 상태를 잃게 됩니다. 

 이런 변화뿐만 아니라 앱이 백그라운드에 있을 때 시스템의 리소스가 부족해지면 앱이 정리되어 이 또한 앱의 상태를 잃게 됩니다.(다른 앱과 상호작용해야 하기 떄문에) 

 `app dismissal`이 되면(앱이 종료되면) 또한 앱은 상태를 잃게 됩니다.


![](https://velog.velcdn.com/images/cksgodl/post/dd5baab1-17ae-4da8-aff2-0acaed9cea83/image.png)


# Android에서 UI 상태를 저장하는 모범 사례 


## ViewModel를 활용하기

Android에서는 뷰모델을 활용하여 State를 관리하라고 권장하고 있습니다.

해당 이유는 다음과 같습니다.

![](https://velog.velcdn.com/images/cksgodl/post/c6b8f382-416e-4516-bd77-5f0b578ff5ce/image.png)

* `ViewwModel`은 `configuration changes`에도 살아남습니다.
* 살아남은 `State`는 메모리 내부에 유지되게 됩니다.
* 또한 뷰모델은 사용 가능한 메모리에 의해 제한되며 메모리에 저장하기에 읽고 쓰기가 빠릅니다. * `Jetpack Navigation`은 해당 화면이 백스택에 존재하면 뷰모델의 상태를 캐싱해 둡니다.

실제 구글 I/O에서 제공한 예는 다음과 같습니다.
```kotlin
class InterestesViewMdoel(
	authorsRepository : AuthorsRepository,
    topicsRepository: TopicsRepository
) : ViewModel() {

	val uiState = combine(
    	authorsRepository.getAuthorsStream(),
    	topicsRepository.getTopicsStream(),
    ) { availableAuthors, availableTopics ->
    	InterestsUiState.Interests(availableAuthors, availableTopics)
    }.stateIn(
    	scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = InterestsUiState.Loading
    )
}
```

해당 뷰모델의 예제는 다음과 같은 목적을 위해 사용됩니다.
1. 데이터를 만들기 위한 장치로
2. `config changes`로부터 살아남기 위해
3. `Screen-level`단계의 `state holder`로써 데이터를 방출하기 위해

> 따라서 뷰모델을 `state holder`로써 사용하지 않는 것은 좋지 않습니다!

## 예기치 못한 앱 종료(Unexpected app dismissal)가 일어날 땐?

 사용자가 메뉴버튼을 눌러 앱을 종료하던가, 핸드폰을 강제로 종료한다든가 등의 예기치 못한 앱 종료에서 State를 어떻게 관리해야 할까요?
 
 ## 영구 저장장치(Persistent Storage) 사용 하기
 
 ![](https://velog.velcdn.com/images/cksgodl/post/55e65cc2-76ab-4de7-99a0-9389905475f4/image.png)

`Android Jetpack`에서는 이를 위해 2가지 옵션을 제공합니다.

* DataStore
	작거나 간단한 데이터를 저장하는데 활용하세요.

* Room
	복잡하거나 관계있는 데이터 계층을 저장하거나, 데이터에 업데이트가 필요할 경우 사용하세요.

필요한 상황에 따라 맞는 라이브러리를 활용하도록 하세요.
    
    
![](https://velog.velcdn.com/images/cksgodl/post/344b6f9b-f030-4244-a05c-1236f23a37ef/image.png)

* `configuration changes`에서 살아남습니다!
* 영구 저장소는 `Memory`에 저장되는 것이 아닌 `Disk`에 저장되게 됩니다. 
* `disk space`에 제한이 걸리게 되며 디스크에 저장되기에 읽고 쓰는것이 느립니다.
* 앱의 데이터의 저장에 용이합니다.


## Saved State Apis활용하기

프로세스가 종료되면 모든 `ViewModel`의 모든 `State`는 날라가게 됩니다. 그렇다고 `Persistent Storage`를 활용하기엔 읽고 쓰는 속도가 느리기에 적합하지 않습니다.

따라서 안드로이드에서는 에센셜한 `State`를 앱이 꺼져도 저장할 수 있도록 `Saved State Api`를 제공합니다.

![](https://velog.velcdn.com/images/cksgodl/post/b6f9e111-8a77-4309-99e8-da544216e45f/image.png)

* `configuration changes`로부터 안전합니다.
* 데이터를 직렬화 하여 프로세스 외부의 메모리에 저장합니다.
* 직렬화한 데이터는 번들로 저장되며 번들은 `50KB`미만으로 저장하기를 권장합니다.
* 직렬화를 진행하기에 속도가 느릴 수 있습니다.
* 큰 오브젝트나 리스트를 저장하지 마세요. 직렬화는 많은 메모리를 잡아 먹습니다!
* 탐색 또는 사용자 입력에 따라 달라지는 일시적인 상태를 저장하기에 적합합니다!
-> 예를 들면 스크롤의 포지션, `detail Screen`의 아이디 값, `TextField`의 인풋 값 등등을 저장하기에 적합합니다.


사용 가능한 API로는
`Compose`에서는 `rememberSaveable`를 활용할 수 있으며
기존의 `XML`시스템에서는`onSaveInstanceState`를 활용해야 합니다.


다음은 `Compose`에서의 `Saved State`활용 예제입니다.

```
fun ChatBubble(
	messsage : Message
) {

	var showDetails by rememberSaveable { mutableStateOf(false) }
    
    ClickableText(
    	text = AnnotatedString(message.content),
        onClick = { showDetails = !showDetails }
    )

	if(showDetails) {
    	Text(message.timestamp)
    }
}
```


![](https://velog.velcdn.com/images/cksgodl/post/3ec85867-ea9b-492e-9d61-20d7945f532c/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/bedb999d-6dc0-4860-b5fb-429bac094618/image.png)

해당 메시지의 디테일 여부는 `configuration changes`에서도 살아남습니다.

똑같은 예를 `View`시스템에서도 구현해보겠습니다.

```
class ChatBubbleView(context: Context, ...) : View(context) {

	
    private var isExpanded = false
    
    override fun onSaveInstanceState(): Parcelable {
    	super.onSaveInstanceState()
        return bundleOf(IS_EXPANDED to isExpanded)
    }
    
    override fun onRestoreInstanceState(state: Parelable) {
    	isExpanded = (state as Bundle).getBoolean(IS_EXPANDED)
        super.onRestoreInstanceState(null)
    }
    
    companion object {
    	private const val IS_EXPANDED = "is_expanded"
    }
}
```

이러한 [`SavedState`의 테스트 구현](https://youtu.be/V-s4z7B_Gnc?list=PLWz5rJ2EKKc85Xna4Q3Fw79OP_3D1JaJW&t=531)은 다음 링크를 참고해주세요.



## Saved State API를 활용한 비즈니스 로직 구현

```kotlin
class ConversationViewModel(
	savedStateHandle: SavedStateHandle
) : ViewModel() {
	
    var message by savedStateHandle.saveable(stateSaver = TextFieldValue.Saver) {
    	mutableStateOf(TextFieldValue(""))
    }
    	private set
        
        
    fun update(newMessage: TextFieldValue) {
    	message = newMessage
    }
    
    fun send() { // ... // }
    
}

```

`SavedStateHandle`를 활용하여 사용자가 타이핑하고 있는 텍스트를 저장하고 이를 불러옵니다.  `SavedStateHandle`는 `Compose State`도 제공하며 값을 스트림형식으로 제공합니다.(플로우 같이) 

> 기억해야할 점은 `SavedStateHandle`은 엑티비티가 멈췄을 때만 데이터를 저장하기에, 앱이 백그라운드에서 해당 값을 업데이트하면 액티비티가 멈췄을 때의 데이터를 복구한다는 점입니다.



다음은 `SavedState API`의 예제입니다.

![](https://velog.velcdn.com/images/cksgodl/post/590f3b88-a4ba-4275-9405-0ddcb1de46e9/image.png)

비즈니스 로직의 경우 UI 툴킷에 상관없이 `SavedStateHandle`을 활용하면 되겠습니다.


## 실제 동작 소스와 모범 사례

`Compose`에서의 예제입니다.

뉴스 검색 UI를 작성하되 유저의 입력이 재사용이 필요하다고 가정해 봅시다. 

![](https://velog.velcdn.com/images/cksgodl/post/031f290d-43ee-40ba-b6a7-70cab7ea944f/image.png)



```kotlin
class NewsSearchState(
	private val newsRepository: NewsRepository,
    initialSearchInput: String
) {
	var searchInput = mutableStateOf(TextFieldValue(initialSearchInput))
    	private set

	
	companion object {
    	fun saver(newsRepository: NewsRepository): Saver<NewsSearchState, *> = Saver (
        	save = {
            	with(TExtFieldValue.Saver) { save(it.searchInput) }
            },
            restore = {
            	TextFieldValue.Saver.restore(it)?.let { searchInput -> 
                	NewsSearchState(newsRepository, searchInput)
                }
            }
        )
    }

}
```

```kotlin
@Composable
fun rememberNewsSearchState(
	newsRepository: NewsRepository,
    initialSearchInput: String = ""
) {
	return rememberSaveable(
    	newsRepository, initialSearchInput,
        saver = NewsSearchState.saver(newsRepository) // Custom Saver
    ) {
    	NewsSearchState(newsRepository, initialSearchInput)
    }
}
```

해당 예제는 `rememberSaveable`를 활용한 유저의 인풋값을 저장하는 방법입니다. 
`Compose`의 컨벤션에 따라 상태를 저장하는 함수앞에 `remember`이라는 이름을 붙여 함수를 정의했습니다.
`NewsSearchState`라는 복잡한 객체를 저장하고 불러와야하기에 `Custom Saver`를 구현하여 넣어줬습니다. 

> 핵심은 `rememberSaveable`객체이며 해당 함수 내부에서 저장과 복구를 모두 구현하고 있습니다. `androidx/compose/runtime/saveable/RememberSaveable.kt`

이를 활용하는 예로써는 `navigation - NavHost.kt`에서도 바텀 네비게이션의 백스택 엔트리에 따라 동일한 뷰를 보여주는 예제로써 작동하고 있습니다.


---

`XML`를 활용한 뷰 시스템에서의 예제를 봅시다.

```kotlin
class NewsSearchState(
	private val newsRepository: NewsRepository,
    private val initialSearchInput: String,
    registryOwner: SavedStateRegisteryOwner
) : SavedStateRegistry.SavedStateProvider {

    private var currentQuery: String = initialSearchInput

	init {
    	registryOwner.lifecycle.addObserver(LifecycleEventObserver { _, event -> 
        	if (event == Lifecycle.Event.ON_CREATE) {
            	val registry = registryOwner. savedStateRegistry
                if (registry.getSavedStateProvider(PROVIDER) == null) {
                	registry.registerSavedStateProvider(PROVIDER, this)
                }
                val savedState = registry.consumeRestoredStateForKey(PROVIDER)
                currentQuery = savedState?.getString(QUERY) ?: initialSearchInput
            }
        }
    }

    // Rest of business login ...
    
    override fun saveState(): Bundle {
    	return bundleOf(QUERY to currentQuery)
    }
    
    companion object {
    	private const val QUERY = "current_query"
        private const val PROVIDER = "news_search_state"
    }
    
}
```


`SavedStateRegistry`는 상속가능한 인터페이스이며, 다른 컴포넌트가 저장하고, 복구하는 것을 가능하게 해줍니다. 해당 인터페이스를 상속받고 `SavedStateRegisteryOwner`를 활용해 뷰시스템에서도 `SavedState`를 활용할 수 있습니다.

```
class NewsFragment : Fragment() {
	
    private var newsSearchState = NewsSearchState(this)
    // ...
}
```


## 정리


![](https://velog.velcdn.com/images/cksgodl/post/6df3733c-d591-4d7c-a093-dc81e0a4e8c8/image.png)

안드로이드에서 UI를 저장하는 방식 크게 3가지 방식으로 이루어집니다.
* ViewModel
* Saved State
* Persistent Storage

각각 생존시기 및 저장 위치, 권장되는 사용예제들이 정의되어 있으니 각각의 맞는 상황에 맞춰 사용해야합니다.


 