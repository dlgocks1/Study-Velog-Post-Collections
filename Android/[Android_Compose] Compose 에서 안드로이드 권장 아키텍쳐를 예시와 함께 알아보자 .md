# 안드로이드 권장 아키텍처란?

안드로이드에서 권장하는 앱 아키텍처는 다음과 같다.

![](https://velog.velcdn.com/images/cksgodl/post/3bddc64e-edae-4b86-832f-c1963fd5d8d4/image.png)

정확한 내용은 [안드로이드 디벨로퍼 - 앱 아키텍처 가이드](https://developer.android.com/jetpack/guide?hl=ko)을 참고하는 것이 좋고, 간단하게 사용하는 언어로 정리하면 다음과 같다.

* UI Layer - 사용자에게 표시될 뷰를 관리하는 영역
	ex) ViewModel, Composable 등등,,

* Data Layer - 서버, DB등의 외부에서 화면에 필요한 데이터를 가지고 오는 영역
	ex) Repository, Retrofit, RoomDB 등등,,
    
* Domain Layer - 화면에 필요한 데이터를 화면에 맞게 가공하여 전달하는 영역
	ex) Formatter, UseCase 등등,,,
    

설명만 들어서는 무슨 소린지 잘 이해가 가지 않는다. 실제 예제와 함께 아키텍처를 준수한다는 것이 무엇인지 알아보자.


# 예제와 같이 알아보기

Runway 어플리케이션을 개발하며 다음과 같은 화면을 개발해야 했다. 

![](https://velog.velcdn.com/images/cksgodl/post/2a838639-9e30-47ff-ada8-2566c05a0cb8/image.png)

화면에 들어갈 기능이 무엇이 있는가?

1. 나의 프로필 이미지, 닉네임 가져오기 및 편집하기
2. 나의 후기, 북마크된 저장 데이터 가져오기

등이 있을 수 있다.

해당 기능을 구현하기 위해 어떻게 해야 할까?


## 1. 뷰 구성 - UI Layer

기본 컴포즈의 뷰작성은 다음과 같다.

```
@Composable
fun MypageScreen(appState: ApplicationState) {

	val userNickname by remember {
    	mutableStateOf("기본 닉네임")
    }
    // ...

    LaunchedEffect(key1 = Unit) {
        // 초기 사용자 정보 가져오기
    }

    Column(modifier = Modifier.fillmaxSize()) {
        Text(text = userNickname)
    	// 뷰 관련된 내용 작성...
    }
```

`State`객체를 활용하여 뷰에 보여줄 데이터를 담아 변경해주면 이를 알아서 Observe해주며 이를 업데이트 한다. `(Recomposition)`

`State`를 `remember API`를 활용하여 `Composable`내부에 저장할 수도 있겠지만, `ViewModel`에도 저장할 수 있다.

* Composable에 저장하는 경우, 스크린 내부에서 결정되는 상태를 저장할 때만 사용하는 것이 좋다.
_예를 들어 드롭박스가 활성화 상태, `BottomSheet`가 올라왔는지 등 뷰 자체의 상태_
![](https://velog.velcdn.com/images/cksgodl/post/8f9d0f5d-83e1-4a3c-bd2e-172dc16ecfae/image.png)

```
val isDropboxDown by remember {
	mutableStateOf(false)
}

if(isDropboxDown) {
	// Dropbox가 내려갔을 때 화면
} else {
	// Dropbox가 올라와 있을 때 화면
}

```

* `ViewModel`을 활용하여 `State`를 저장하는 경우는 뷰 외부에서 데이터를 불러와야하는 경우일 때이다.
_예를 들어 DB에서 데이터를 불러와야 한다던가, 서버에서 데이터를 불러와야 한다든가 등등,,,_ 

```
// In ViewModel
private val _someUserData = mutableStateOf("")
val someUserData: State<String> get() = _someUserData

// In Composable
private val viewModel: SomeViewModel = hiltViewModel()
Text(text = viewModel.someUserData.nickname) 
```

---

또한 `State`뿐만 아니라 `Flow`또한 `State`로 변환하여 리컴포지션을 발생시킬 수 있다.

```
// https://developer.android.com/jetpack/compose/state?hl=ko
dependencies {
      ...
      implementation("androidx.lifecycle:lifecycle-runtime-compose:2.6.0-beta01")
}

// In ViewModel
val someUserData:MutableStateFlow<String> = MutableStateFlow("기본 이름 값")

// In Composable
val someUserData: State<String> = viewModel.someUserData.collectAsLazyPagingItems()
```

이런 `Flow`의 변환은 확장함수인 `combine`과 같이 사용될 때 그 진가를 발휘한다.

다음 예는 닉네임과 프로필 이미지를 `combine`을 활용해 `UiState` 데이터 클래스로 감싸서 관리하는 예제이다.
 
 * Data Class - UiState
```
data class ProfileImageUiState(
    val profileImage: ProfileImageType = ProfileImageType.DEFAULT,
    val nickName: Nickname = Nickname.default(),
)
```

* In ViewModel

```
private val _nickName = MutableStateFlow(Nickname.default())
private val _profileImage = MutableStateFlow<ProfileImageType>(ProfileImageType.DEFAULT)

val profileImageUiState: StateFlow<SignInProfileImageUiState> =
	// 프로필 이미지와, 닉네임이 플로우가 변할 시 이를 collect하여 다음 객체를 뱉어낸다. 
    combine(_profileImage, _nickName) { profileImage, nickName ->
        ProfileImageUiState(profileImage = profileImage, nickName = nickName)
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = ProfileImageUiState()
    )
```


* In Composable

```
val profileImageUiState = viewModel.profileImageUiState.collectAsStateWithLifecycle()

MainProfileInfo(
    nickName = profileImageUiState.value.nickName.text,
    profileImage = profileImageUiState.value.profileImage,
    navigateToEditProfile = {
        appState.navigate(EDIT_PROFILE_IMAGE_ROUTE)
    }
)
```

해당 방식을 사용하면 `State`와 `Flow`를 활용하여 컴포즈에서 뷰를 업데이트할 수 있다.

## 2. 데이터 불러오기 - Data Layer

> 이후의 내용은 Hilt를 활용해 DI를 구현하고 있다.

### Retrofit2 서비스 선언

1. Retrofit2를 활용할 네트워크 인터페이스(서비스)를 선언한다.
_모든 네트워크 응답을 비동기로 관리할 것이기 때문에 `Resepons`와 `suspend`키워드를 붙여준다._
```
interface AuthService {

    /** 마이페이지 조회 */
    @GET("/users")
    suspend fun getMyInfo(): NetworkResponse<MyPageInfo>
}
```

현재 서버에서의 응답이 기본적으로 다음과 같이 제공되기에 
```
{
  "code": "1000",
  "isSuccess": true,
  "message": "요청에 성공하였습니다.",
  "result": "응답 결과"
}
```

_+) `NetwrokResponse<T>`는 다음과 같이 선언되어있다._
```
typealias NetworkResponse<T> = Response<ResponseWrapper<T>>

// Generic을 활용하여 모든 응답을 감싸는 ResponseWrapper를 활용한다.
@JsonClass(generateAdapter = true)
data class ResponseWrapper<out T>(
    val code: String,
    val isSuccess: Boolean,
    val message: String,
    val result: T
)
```



2. 해당 서비스를 감싸는 `Client`를 따로 선언해준다.

이렇게 따로 `Client`를 선언하는 이유는 변경을 최소화 할 수 있기 때문이다.

서비스의 함수를 여러 레포지토리에서 사용한다고 Service를 그대로 사용하게 되면 해당 서비스 함수의 수정 시에 모든 레포지토리의 함수를 수정해야 한다. 
>즉 불필요한 시간이 소요될 가능성이 크다. 

```
class RunwayClient @Inject constructor(
    private val authService: AuthService,
) {
    /** Auth */
    suspend fun getMyInfo() = authService.getMyInfo()
}
```

3. 해당 서비스에 `Hilt`를 활용해 종속성을 주입한다.

```

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    private val httpLoggingInterceptor =
        HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BODY)

    @RunwayInterceptorOkhttpClient
    @Provides
    fun provideRunwayInterceptorOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(httpLoggingInterceptor)
            .authenticator(TokenAuthenticator())
            .addInterceptor(ServiceInterceptor())
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(20, TimeUnit.SECONDS)
            .writeTimeout(20, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()
    }

    @Provides
    @RunwayRetrofit
    fun provideRunwayRetrofit(
        @RunwayInterceptorOkhttpClient okHttpClient: OkHttpClient,
    ): Retrofit {
        return Retrofit.Builder()
            .client(okHttpClient)
            .baseUrl(BuildConfig.BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthService(
        @RunwayRetrofit retrofit: Retrofit,
    ): AuthService {
        return retrofit.create(AuthService::class.java)
    }

    @Provides
    @Singleton
    fun provideRunwayClient(
        authService: AuthService,
    ): RunwayClient {
        return RunwayClient(
            authService = authService,
        )
    }
}
```

이제 `Retrofit2`객체를 활용하여 네트워크 요청을 보낼 준비가 완료되었다.

### Repository에서 네트워크 로직 구현

AuthRepository를 선언하여 내 데이터를 불러오는 로직을 작성한다.

```
interface AuthRepository {

    fun getMyInfo(): Flow<ApiWrapper<MyPageInfo>>
}
```

>_`ApiWrapper`는 다음과 같이 선언되어 있다._

네트워크 요청의 성공, 실패, 응답하지 않음을 분기하기 위한 `sealed class`인 `ApiState`를 선언하여 네트워크 요청을 관리한다.
```
typealias ApiWrapper<T> = ApiState<ResponseWrapper<T>>

sealed class ApiState<out T : Any> {
    data class Success<T : Any>(val data: T) : ApiState<T>()
    data class Error(val errorResponse: ErrorResponse) : ApiState<Nothing>()
    data class NotResponse(val message: String?, val exception: Throwable? = null) :
        ApiState<Nothing>()

    object Loading : ApiState<Nothing>()

    fun onSuccess(onSuccess: (T) -> Unit) {
        if (this is Success) {
            onSuccess(this@ApiState.data)
        }
    }

    fun onError(onError: (ErrorResponse) -> Unit) {
        if (this is Error) {
            onError(this@ApiState.errorResponse)
        }
        if (this is NotResponse) {
            onError(ErrorResponse("500", false, "네트워크 오류가 발생했습니다."))
        }
    }

    fun onLoading(onLoading: () -> Unit) {
        if (this is Loading) {
            onLoading()
        }
    }
}
```

해당 인터페이스의 구현체는 `AuthRepositoryImpl`에 구현해준다.

```
class AuthRepositoryImpl @Inject constructor(
    private val runwayClient: RunwayClient,
) : AuthRepository {

	override fun getMyInfo(): Flow<ApiWrapper<MyPageInfo>> = safeFlow {
        runwayClient.getMyInfo()
    }
}
```
> _safeflow 확장함수는 다음과 같이 선언되어 있다._

```
fun <T : Any> safeFlow(apiFunc: suspend () -> Response<ResponseWrapper<T>>): Flow<ApiState<ResponseWrapper<T>>> =
    flow {
        try {
            val res = apiFunc.invoke()
            if (res.isSuccessful) {
                emit(ApiState.Success(res.body() ?: throw NullPointerException()))
            } else {
                val errorBody = res.errorBody() ?: throw NullPointerException()
                emit(ApiState.Error(GsonHelper.stringToErrorResponse(errorBody = errorBody.string())))
            }
        } catch (e: Exception) {
            emit(ApiState.NotResponse(message = e.message ?: "", exception = e))
        }
    }.flowOn(Dispatchers.IO)
```

`Api`람다식을 실행한 후 그 결과값을 `ApiState`로 감싸주어 `emit`한다.

---

이렇게 `Repository`의 구현이 모두 끝났다. 이제 이에 종속성을 주입해 보자.

```
@Module
@InstallIn(ViewModelComponent::class)
abstract class RepositoryModule {

    @Binds
    @ViewModelScoped
    abstract fun bindsAuthRepository(
        authRepositoryImpl: AuthRepositoryImpl,
    ): AuthRepository
    
}
```

## 3. UI Layer와 Data Layer 연결하기

뷰모델과 Repository를 다음과 같이 연결하여 전달받은 데이터를 활용하면 된다.

* ViewModel

```
@HiltViewModel
class MypageViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

	// ...

	fun getMyProfile() = viewModelScope.launch {
        authRepository.getMyInfo().collect { apiState ->
            apiState.onSuccess {
                updateNickName(it.result.nickname)
                updateProfileImage(it.result.imageURL)
            }
        }
    }
}
```

* Composable

```
val profileImageUiState = viewModel.profileImageUiState.collectAsStateWithLifecycle()

LaunchedEffect(key1 = Unit) {
	viewModel.getMyProfile()
}
```

## 3.5 Usecase 도입 - Domain Layer

개발을 진행하며 `AuthRepository`에 포함된 함수 (역할)이 많아지며 이에대한 의존성이 커짐을 느꼈다. 

![](https://velog.velcdn.com/images/cksgodl/post/5f3afb64-8870-4272-a4fd-0313522a372c/image.png)

이를 해결하기위해 `UseCase`를 활용하는 방법을 알아보자.

_ 도입 배경_

`AuthRepository`에서는 토큰관리, 로그아웃, 탈퇴, 정보가져오기 등 너무 많은 역할을 수행하고 있다. 이를 `ProfileRepository`와 같이 레포지토리를 하나 더 만들어 역할을 가볍게 할 수도 있겠지만, `UseCase`를 활용하여 의존성을 낮출 수도 있다.

>`Usecase`란?
사용자가 서비스에서 수행하고자 하는 것들의 모음을 의미한다.
예를 들어 마이페이지에서는 내 프로필 조회, 리뷰 가져오기와 같이 2가지 서비스를 수행해야 한다.


### 실제로 적용해보기

1. Usecase 인터페이스 선언
해당 서비스에서 수행하고자 하는 것들을 모아 `UseCase`를 선언한다.
_다음 예에서는 데이터레이어에서의 결과값을 페이징형태로 바꾸어주는 함수를 선언한다._
```
interface GetMyProfileDataUseCase {

    fun myReviewPaging(): Flow<PagingData<MyReviewsItem>>

    fun bookmarkedStorePaging(): Flow<PagingData<StoreMetaDataItem>>

    fun bookmarkedReviewPaging(): Flow<PagingData<MyReviewsItem>>

}
```

2. Usecase 구현체 선언
	해당 구현체에서 `AuthRepository`를 활용하여 한단계 구현한다.
    _또한 해당 함수는 Data-Layer에서 가져온 데이터를 `Pager`형태에 맞추어 새롭게 가공해 줌으로 Domain-Layer로 추출하는 것이 좋다._

```
class GetMyProfileDataUseCaseImpl @Inject constructor(
    private val authRepository: AuthRepository,
    private val context: Context,
    private val ioDispatcher: kotlinx.coroutines.CoroutineDispatcher,
) : GetMyProfileDataUseCase {
    override fun myReviewPaging(): Flow<PagingData<MyReviewsItem>> = Pager(
        config = PagingConfig(
            pageSize = 10,
        ),
        pagingSourceFactory = {
            MyReviewPagingSource(
                authRepository = authRepository
            )
        },
    ).flow.flowOn(ioDispatcher)

    override fun bookmarkedStorePaging(): Flow<PagingData<StoreMetaDataItem>> {
        return Pager(
            config = PagingConfig(
                pageSize = 10,
            ),
            pagingSourceFactory = {
                BookmarkedPagingSource(
                    authRepository = authRepository
                )
            },
        ).flow
    }

    override fun bookmarkedReviewPaging(): Flow<PagingData<MyReviewsItem>> = Pager(
        config = PagingConfig(
            pageSize = 10,
        ),
        pagingSourceFactory = {
            BookmarkedReviewPagingSource(
                authRepository = authRepository
            )
        },
    ).flow.flowOn(ioDispatcher)
}
```

3. 종속성 주입
	`Hilt`를 활용하여 종속성을 주입한다.

```
@Module
@InstallIn(ViewModelComponent::class)
object UseCaseModule {

    @Provides
    @ViewModelScoped
    fun provideGetMyProfileDataUseCase(
        authRepository: AuthRepository,
        @ApplicationContext context: Context,
        @DispatcherModule.IoDispatcher ioDispatcher: kotlinx.coroutines.CoroutineDispatcher,
    ): GetMyProfileDataUseCase {
        return GetMyProfileDataUseCaseImpl(
            authRepository = authRepository,
            context = context,
            ioDispatcher = ioDispatcher,
        )
    }
}
```

4. 뷰모델에서의 사용
	뷰모델에서 `Authrepository`를 활용하는 것이 아닌 `UseCase`를 활용함으로 어떤 서비스를 제공하는지 정확히 알 수 있고, `AuthRepository`에 대한 의존성을 줄일 수 있다.

```
@HiltViewModel
class MypageViewModel @Inject constructor(
    private val editMyProfileUseCase: EditMyProfileUseCase,
    private val getMyProfileDataUseCase: GetMyProfileDataUseCase,
) : ViewModel() {

	// ...

	fun getBookmarkedReview() = viewModelScope.launch {
        getMyProfileDataUseCase.bookmarkedReviewPaging().cachedIn(viewModelScope).collect {
            _bookmarkedReview.value = it
        }
    }
}
```


---


## 결론

사이드 프로젝트를 진행하며 최대한 안드로이드 권장 아키텍처를 맞추어 프로젝트를 진행해 보았다. 해당 구조가 완벽한 정답은 아닐수도 있지만, 여러 프로젝트를 거쳐가며 점점 더 정교화되고 적어도 내가 진행한 프로젝트 구조 중 가장 안드로이드 권장 아키텍쳐에 맞는 구조이지 않을까 싶다.

이런 초기에 코드를 세팅하는 것은 어렵고 복잡한 일이지만, 한번 만들어놓고 나면 이후 수정하거나 디벨롭할 때 전보다 훨씬 용이하다. 

해당 프로젝트에 대한 모든 소스는 [Github-Runway](https://github.com/FashionWeek-Runway/Runway-Android)에서 확인이 가능하다.






## 참고자료

[[Android] Clean Architecture - UseCase 란 ?](https://heegs.tistory.com/58)


