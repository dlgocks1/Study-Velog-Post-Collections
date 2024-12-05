Compose를 개발하다 보면 컴포즈 내부에 차곡차곡 쌓이는 `State`를 볼 수 있다.

이를 체계적으로 또 효율적으로 관리해보자.

```
@HiltViewModel
class MypageViewModel @Inject constructor() : ViewModel() {

    private val _userInfo = mutableStateOf(UserInfo())
    val userInfo: State<UserInfo> = _userInfo

    private val _userCocktailWeight = mutableStateOf(UserCocktailWeight())
    val userCocktailWeight: State<UserCocktailWeight> = _userCocktailWeight

}

@Composable
fun ModifyNicknameScreen(
    navController: NavController = rememberNavController(),
    scaffoldState: ScaffoldState,
) {
    val scope = rememberCoroutineScope()
    val focusRequest = remember {
        FocusRequester()
    }
    var textFieldValue = remember {
        val initValue = ""
        val textFieldValue =
            TextFieldValue(
                text = initValue,
                selection = TextRange(initValue.length),
            )
        mutableStateOf(textFieldValue)
    }
    
    Column() { 
	    // ...
    }
}
```

위의 짧은 소스만 보아도 코루틴을 저장하는 `scope`, `scaffoldState`, `navController`, `focusRequest`, `textVfiledValue` 등의 많은 스테이트를 저장하고 또 기억하고 있다.

이러한 `State`는 다음과 같이 나눌 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/676e5c6e-745b-4b21-bdd0-f03fe856017c/image.png)

* `App`전체를 관리하는 `navContoller`, `scaffoldState`

* Data Layer로부터 비즈니스 로직의 `State`를 관리하는 `userInfo`, `userCocktailWeight`

* 사용자로부터 Screen UI 로직의 `State`를 관리하는 `scope`, `textFieldValue`

![](https://velog.velcdn.com/images/cksgodl/post/d4f3d7c2-7587-4adb-9b6a-e73c9262547b/image.png)


## 비즈니스로직과 Screen level의 state holder로는 AAC ViewModel을 활용하라

비즈니스 로직에 관련된 `state`는 화면 회전, 생명주기에 살아 남는 `AAC ViewModel`을 사용할 것을 권장한다.

```
@HiltViewModel
class MypageViewModel @Inject constructor(
    private val userInfoRepository: UserInfoRepository,
) : ViewModel() {

    private val _userInfo = mutableStateOf(UserInfo())
    val userInfo: State<UserInfo> = _userInfo

    private fun getUserInfo() = viewModelScope.launch {
        userInfoRepository.getUserInfo().collectLatest {
            it?.let {
                _userInfo.value = it
            }
        }
    }
    // ...
    
}
```

이러한 뷰모델은 몇가지 장점이 있다.

1. Survives config changes
	스크린보다 오래 살아남을 수 있다.
    
2. Jetpack Integration
	Jetpack 네비게이션 라이브러리와의 호환 
    백스택에 메모리를 캐쉬하여 사용할 수 있다. (Bottom Navigation 바로 이동할 때 캐쉬된 메모리를 활용하여 바로 화면을 불러올 수 있다.)
    ```
    BottomNavigationItem(
        onClick = {
   	        appState.navController.navigate(screen.route) {
                popUpTo(MAIN_GRAPH) {
                    saveState = true // SavedState
                }
                launchSingleTop = true
                restoreState = true // RestoreState
            }
    	// ...    
    },
    ```
    
이러한 뷰모델은 `Screen Level`에서 사용되어야 하며 변할 수 있는 상황에 대한 데이터를 가져야 한다. 그러나 `lifecycle-related APIs`를 가져서는 안된다. 또한 `Activity`, `Framgent` 등의 화면에서만 사용되어야 한다.

## UI Logic은 컴포저블 자신 또는 plain state holder class를 만들어 관리하라

다음은 컴포저블 자신이 자신의 UI State를 관리한다.

```
@Composable
fun ModifyNicknameScreen() {
    val expanded = remember {
    	mutableStaeOf(false)
    }
    var textFieldValue = remember {
        val initValue = ""
        val textFieldValue =
            TextFieldValue(
                text = initValue,
                selection = TextRange(initValue.length),
            )
        mutableStateOf(textFieldValue)
    }
    
    Column() { 
	    TextField(
        	value = textFiledValue,
            // ...
        )
    }
}
```

하지만 이런 `State`를 따로 관리하는 `StateHolder`를 구현하여 상태를 호이스팅할 수 있다.


* UI단의 StateHolder Class (plain class)
```
@Stable
fun modifyScreenState(
	private val modifyNicknameState: ModifyNicknameState,
) {

	val isExpanded: Boolean
    	get() = modifyNicknameState.textFieldValue.text.isBlank()
    
    fun setExpanded(value: Boolean){
    	modifyNicknameState.expanded.value = value
    }
}
```


* App단의 StateHolder class (plain class)

```
@Stable
class ApplicationState(
    val bottomBarState: MutableState<Boolean>,
    val navController: NavHostController,
    val scaffoldState: ScaffoldState,
) {
	
    val currentDestination: NavDestination?
    	@Composable get() = navController.currentBackStackEntryAsState().value?.destination
        
    val shouldShowBottomBar: Boolean
    	get() = //..
        
	suspend fun showSnackbar(message: String) {
        scaffoldState.showSnackbar(message)
    }
    
    fun navigate() // ...
    
    fun onBackClick() // ...

}
```

이런 `State Holder`(plain class)는 재사용 가능한 UI로직을 관리하기에 추천되며 또한 `lifecycle-related APIs`를 참조할 수 있다.


> State를 관리하는 ViewModel 또는 plain class를 이용해 상태를 호이스팅하여 앱을 관리하라. 
UI 컴포저블은 상태를 관리하지 않고 뷰를 출력하기만 하여 재활용성을 늘린다.

![](https://velog.velcdn.com/images/cksgodl/post/922df651-e3f1-43e8-bea9-3193a61f4492/image.png)


#### `Use ViewModel if its benefits apply to your app`


## Observable data holder을 사용하기

* 다음은 `One-shot APIs`에 대한 `state`관리의 예이다.

```
class DiceRollViewModel : ViewModel() {
	
    private val _uiState = MutableStateFlow(DiceRollUiState())
    private val uiState: StateFlow<DiceRollUiState> = _uiState.asStateFlow()
    
    fun rollDice() {
    	_uiState.update { currentState ->
        	currentState.copy(
            	firstDiceValue = Random.nextInt(1..6),
                secondDiceValue = Random.nextInt(1..6),
                numberOfRolls = currentState.numberOfRools +1
            )
        }
    }
}
```

기존의 `LiveData`, `StateFlow`를 사용할 때는 `프로퍼티`자체에 변화가 있을 때 `Observing`이 되기 때문에 리스트를 저장하고 변화할 때는 다음과 비슷한 꼼수가 필요했다.

```
fun addLiveDataList(someData: Int) {
	_someLiveData.value.add(someData)
    _someLiveData.value = _someLiveData.value
}
```

하지만 컴포즈에서는 해당 `StateList`를 제공하고 있다. 

```
private val _someList = mutableStateListOf<Int>()
val someList: State<Int> get() = _someList
```


---

* 다음은 `Streams of data`의 `state`관리의 예이다.

```
class DiceRollViewModel(
	userRepository: UserRepository
) : ViewModel() {
	
    val userUiState: StateFlow<String> =
    	userRepository.userStream.map { user -> user.name }
      	.stateIn(
        	scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = ""
        )
}
```

`SharingStarted.WhileSubscribed(5000)`으로 지정한 이유는 화면이 꺼져도 5초 동안은 플로우를 유지하라 라는 뜻이다. 

이렇게 `Data-Layer`단에서 `flow`를 받아온 후 이를 컴포저블에서 사용해보자

```
// State holder
@Composable
fun DiceRollUI(viewModel: DiceRollViewModel = viewModel()) {
	val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    DiceRollUI(uiState, { viewModel.rollDice() }
}

// UI 뷰 로직
@Composable
fun DiceRollUI(uiState: DiceRollUiState, onRollDice: () -> Unit) {
	Column() {
    	when (uiState) {
        	is Success -> {
            	Text(uiState.firstDiceValue.toString())
            }
        }
    }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/4de75dba-c36d-4f67-9896-8ae7066a91ca/image.png)

# result Intent를 Compose에서 구현하는 방법?

컴포즈 네비게이션에서는 `navController`내부의 `entry`를 활용하여 뷰모델을 생성할 수 있다.

```
fun NavGraphBuilder.onboardGraph(appState: ApplicationState) {
    navigation(startDestination = ScreenRoot.ONBOARD_START, route = ScreenRoot.ONBOARD_GRAPH) {
    
        composable(ScreenRoot.ONBOARD_START) { entry ->
            val backStackEntry = remember(entry) {
                appState.navController.getBackStackEntry(ScreenRoot.ONBOARD_GRAPH)
            }
            val onboardViewModel: OnboardViewModel = hiltViewModel(backStackEntry)
            OnboardStartScreen(appState.navController, onboardViewModel = onboardViewModel)
        }
        
        composable(ScreenRoot.ONBOARD_NICKNAME) {
            val backStackEntry = remember(it) {
                appState.navController.getBackStackEntry(ScreenRoot.ONBOARD_GRAPH)
            }
            val onboardViewModel: OnboardViewModel = hiltViewModel(backStackEntry)
            OnboardNicknameScreen(
                appState.navController,
                onboardViewModel = onboardViewModel,
                scaffoldState = appState.scaffoldState,
            )
        }        
        // ...

}
```
이를 통해 `navigtaion graph`내부에서 같은 뷰모델을 공유할 수 있으며 이를 통해 `return intent`와 비슷하게 작동하는 로직을 작성할 수 있다.


---


다른 방법으로는 `navController`의 `entry`에 직접적으로 데이터를 넣을 수도 있다.

예를 들어 `A -> B`라는 히스토리를 가진 상태에서 B에서 다음 버튼을 클릭한다. 
```
Button(
	onClick = {
        appState.navController.previousBackStackEntry
            ?.savedStateHandle
            ?.set(
                "bitmap_images",
                viewModel.selectedImages.toList(),
            )
            
            appState.navController.popBackStack()
		}
```

`A`는 현재 `backStackEntry` 내부의 저장된 정보를 다음과 같이 받아올 수 있다.

```
val result = appState.navController.currentBackStackEntry
    ?.savedStateHandle
    ?.getLiveData<List<ReviewViewModel.CroppingImage>>("bitmap_images")
    ?.observeAsState()
```

이것이 가능한 이유는

`SavedStateHandle`내부에서 `liveData`와 `flow`를 Map형태로 저장하고 있기 때문이다. 
```
class SavedStateHandle {
    private val regular = mutableMapOf<String, Any?>()
    private val savedStateProviders = mutableMapOf<String, SavedStateRegistry.SavedStateProvider>()
    private val liveDatas = mutableMapOf<String, SavingStateLiveData<*>>()
    private val flows = mutableMapOf<String, MutableStateFlow<Any?>>()

	// ...
    
    private fun <T> getLiveDataInternal(
        key: String,
        hasInitialValue: Boolean,
        initialValue: T
    ): MutableLiveData<T> {
        
        // 키 값에 대한 라이브데이터를 가져온다.
        
        return mutableLd
    }
}
```




## 참고 자료

[State holders and state production in the UI Layer](https://www.youtube.com/watch?v=pCX9wvu-Bq0&t=1097s)

[상태 홀더 및 UI 상태](https://developer.android.com/topic/architecture/ui-layer/stateholders)