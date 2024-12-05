## Retrofit2에서 Call과 Response의 차이점

[call or response in Retrofit?](https://stackoverflow.com/questions/64124670/call-or-response-in-retrofit)

네트워크 연결을 도와주는 retrofit라이브러리에서는 결과값을 감싸주는 Wrapper클래스로 Call클래스와 Response클래스를 지원해준다. 그렇다면 두 클래스의 차이는 무엇이고 어떤 것을 사용해야 할까?

* Call 클래스

`Call`클래스를 사용하면 `enqueue callback`함수를 사용할 수 있으며 이는 비동기작업이 아닌 동기적인 작업을 수행할 때 용이하다. 

```
@POST("custom_URL")
fun getMovies(
	@BODY("params") params: Params,
): Call<DataResponse>
```

```
service.networkRequest(params)
    .enqueue(object : Callback<DataResponse> {
        override fun onResponse(
            call: Call<DataResponse>,
            response: Response<DataResponse>
        ) {
            TODO("네트워크 요청이 성공했을 때")
        }

        override fun onFailure(call: Call<DataResponse>, t: Throwable) {
            TODO("네트워크 요청이 실패했을 때")
        }

    })
```

* Response 클래스

그러나 코루틴이나 RxJava와 같은 비동기 작업을 수행할 때에는 `enqueue callback`(콜백함수)가 필요하지 않으며, 결과값만 사용하면 되기 때문에 `Response`클래스를 사용하자.

```
@POST("custom_URL")
fun getMovies(
	@BODY("params") params: Params,
): Response<DataResponse>
```

```
suspend fun getMovies(): List<Movie> {
        lateinit var movieList: DataResponse
        try {
            val response = service.getMovies()
            val body = response.body()
            if(body!=null){
                movieList = body.movies
            }
        } catch (exception: Exception) {
            Log.i("MyTag", exception.message.toString())
        }
        return movieList
    }  
```
![](https://velog.velcdn.com/images/cksgodl/post/10b199a2-e14f-4b28-bfbe-db084da1daa5/image.png)

Response를 사용하면 try - catch로 따로 에러를 핸들링 해주어야 한다.
또한 반환된 결과에 따라 `.body()`, `.isSuccessful`등과 같은 유틸리티 함수를 제공해주며 이를 사용해 원하는 작업을 수행하면 된다.

---

그렇다면 이러한 `Reponse`를 사용해 네트워크 요청을 비동기로 다루어 보자.

### API에 대한 결과를 Sealed 클래스로 감싸기

```
sealed class ApiResult<out T> {
    data class Success<out T>(val value: T) : ApiResult<T>()
    object Empty : ApiResult<Nothing>()
    data class Error(
        val exception: Throwable? = null,
        var message: String? = ""
    ) : ApiResult<Nothing>() // data class를 사용하지 않으면 따로 equals 및 hascode 함수를 구현해야 한다.
    
    fun handleResponse(
        emptyMsg: String = "결과 값이 없어요.",
        errorMsg: String = "인터넷 상태를 확인해주세요.",
        onError: (String) -> Unit,
        onSuccess: (T) -> Unit,
    ) {
        when (this@ApiResult) {
            is Success -> onSuccess(this@ApiResult.value)
            is Empty -> handleException {
                onError(emptyMsg)
            }
            is Error -> handleException(exception) {
                onError(errorMsg)
            }
        }
    }

    private fun handleException(
        exception: Throwable? = null,
        onError: () -> Unit,
    ) {
        exception?.printStackTrace()
        onError()
    }
}
```
다음과 같은 `ApiResult` 클래스를 생성하여 API에서 반환되는 결과값을 Wrap하여 사용한다. 
`handleResponse`는 결과 값을 처리하는 소스에서 다룬다. 아래에서 다시 언급.


### (Domain Layer) `flow`로 반환해주는 함수로 네트워크 요청을 관리

```
fun <T> safeFlow(apiFunc: suspend () -> Response<T>): Flow<ApiResult<T>> = flow {
    try {
        val res = apiFunc.invoke()
        if (res.isSuccessful) {
            val body = res.body() ?: throw java.lang.NullPointerException()
            emit(ApiResult.Success(body))
        }
    } catch (e: NullPointerException) {
        emit(ApiResult.Empty)
    } catch (e: HttpException) {
        emit(ApiResult.Error(exception = e))
    } catch (e: Exception) {
        emit(ApiResult.Error(exception = e))
    }
}
```
retrofit의 네트워크 요청 <-> flow로 반환하여 주는 함수를 작성한다.
해당 함수에선 `Response<T>`로 결과값이 반환되기 때문에 `.isSuccessful`를 사용하여 성공했는지, `.body()`가 null이 아닌지 체크 후 리턴되는 반환 값을 emit한다.

### Repository (Data Layer)단에서 API를 요청
```
fun getMovies(
	params: Params,
): Flow<ApiResult<DataResponse>> = safeFlow {
	service.getMovies(params = Params)
}
```

### ViewModel (UI Layer)단에서 결과 값 처리
```
suspend fun getMovies(
	params: Params,
    onError: (String) -> Unit
) = viewModelScope.launch {
    repository.getMovies(
		params: Params,
    ).collectLatest { result ->
        result.handleResponse(onError = onError) { res ->
        	// onSuccess일 때
            when (res.response_code) {
                200 -> {
                    _moviesList.value = res.moviesList
                }
                else -> {
                    onError("요청 값이 잘못됬습니다.")
                }
            }
        }
    }
}
```
`Sealed`클래스에서 정의된 handleResponse를 사용하여 해당 다시 한번 더 분기 처리를 해주었다. 이렇게 정의한 이유는 
```
{
	response_code : 200,
    bodyResponse : { // Body... }
}
```
현재 결과 값으로 오는 네트워크 요청 반환 값이 위와 같은 형식으로 오기 때문에 http code가 아닌 자체적인 내부 `response_code`로 한번 더 분기를 나누어 주었다.
+) 함수의 마지막 인자로 오는 익명함수(람다)는 바깥으로 빼서 사용할 수 있다.

```
fun handleResponse(
    emptyMsg: String = "결과 값이 없어요.",
    errorMsg: String = "인터넷 상태를 확인해주세요.",
    onError: (String) -> Unit,
    onSuccess: (T) -> Unit,
) {
    when (this@ApiResult) {
        is Success -> onSuccess(this@ApiResult.value)
        is Empty -> handleException {
            onError(emptyMsg)
        }
        is Error -> handleException(exception) {
            onError(errorMsg)
        }
    }
}
```


## 로딩 처리

해당 API를 실행하며 로딩처리를 수행하려면 flow의 `onStart` 및 `onComplete`를 사용한다.
```
 flowOf("a", "b", "c")
    .onStart { emit("Begin") }
    .collect { println(it) } // prints Begin, a, b, c
    
 flowOf("a", "b", "c")
     .onCompletion { emit("Done") }
     .collect { println(it) } // prints a, b, c, Done
```
 
flow를 Collect하기 전, collect가 끝난 후에 실행되는 함수로써 이것을 사용하면 간단하게 로딩을 구현할 수 있다.

---

* (Ul Layer)로딩중임을 나타내는 상태를 선언한다.

```
private val _isLoading: MutableLiveData<Boolean> = MutableLiveData(false)
val isLoading: LiveData<Boolean> get() = _isLoading

// 로딩상태를 바꾸어주는 함수
private fun isLoading(): Unit = run { _isLoading.value = true }
private fun onComplete(): Unit = run { _isLoading.value = false }
```

* (View) View에서 해당 상태를 옵저빙하며 뷰 관리

```
viewModel.isLoading.observe(this) {
    it?.let {
        if (it) {
            // TODO : Loading 중일 때의 Viwe 설정
            return@let
        }
        // TODO : Loading 중이 아닐 때의 Viwe 설정
    }
}
```

* (UI Layer) API를 요청하는 함수단에 콜백함수로 같이 제공하기

```
suspend fun getMovies(
    params: Params,
    onError: (String) -> Unit
) = viewModelScope.launch {
    repository.getMovies(
	    params: Params,
        onLoading = ::isLoading,
        onComplete = ::onComplete
    ).collectLatest { result ->
    	// ...
    }
```

* (Data Layer) Repository에서 flow를 수집할 때, 끝났을 때 해당 콜백함수 실행

```
fun getMovies(
    params: Params,
    onLoading: () -> Unit = {},
    onComplete: () -> Unit = {},
): Flow<ApiResult<DataResponse>> = safeFlow {
    service.getMovies(params = Params)
}.onStart { onLoading() }.onCompletion { onComplete() }
```

이러한 방식의 로딩처리는 콜백함수가 많이 들어가기 때문에 아규먼트가 많아져 가독성이 떨어지고 복잡하다. 또한 Single Activity Architecture같이 단순한 구조가 아니라면 뷰마다 로딩에 관련된 로직을 처리하여야 한다.

더 좋은 로딩처리가 있다면 다시 포스팅하기



참고 자료 :

https://heeeju4lov.tistory.com/34

https://heeeju4lov.tistory.com/11

https://stackoverflow.com/questions/64124670/call-or-response-in-retrofit