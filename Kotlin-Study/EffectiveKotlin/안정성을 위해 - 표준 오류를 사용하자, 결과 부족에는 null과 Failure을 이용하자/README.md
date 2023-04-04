## 사용자 지정 오류보다 표준 오류를 사용하자.

직접 오류를 정의하여 사용하는 것보다는 최대한 표준 라이브러리의 오류를 사용하는 것이 좋다.

많은 사람들이 잘 알고있는 오류를사용하면 다른 사람들이 API를 더 쉽게 배우고 이해할 수 있다.

일반적으로 사용되는 오류는 다음과 같다.

- IllegalArgumentException, IllegalStateException
  require과 check를 사용해 throw할 수 있는 오류
- IndexOutOfBoundsException
  인덱스 파라미터의 값이 범위를 벗어났다는 것을 나타낸다.
- ConcurrentModificationException:
  동시 수정을 금지했는데, 발생한 것을 의미
- UnsupportedOperationException
  사용하려고 했던 메서드가 현재 객체에서는 사용할 수 없다는 것을 의미
- NoSuchElementException
  사용하려고 했던 요소가 존재하지 않을때 발생한다.
  예를 들어 내부에 요소가 없는 Iterable에 대해 next를 요청했을 때,

## 결과 부족이 발생할 경우 null과 Failur를 사용하자.

함수가 원하는 결과를 만들어 낼 수 없을 때가 종종있다. 다음과 같은 예를 보자.

1. 서버로부터 데이터를 읽어 들이려고 했는데, 인터넷 연결 문제로 읽어 들이지 못한 경우
2. 조건에 맞는 첫 번째 요소를 찾으려 했는데, 조건에 맞는 요소가 없는 경우
3. 텍스트를 파싱해서 객체를 만들려고 했는데, 텍스트의 형식이 맞지 않는 경우

이러한 상황을 처리하는 메커니즘은 크게 다음과 같이 두 가지가 있다.

> 1. null 또는 "실패를 나타내는 sealed 클래스"를 리턴한다.
> 2. 예외를 `throw`한다.

이러한 두 가지는 중요한 차이점이 있다.

일단 예외를 throw하는 것은 정보를 전달하는 방법으로 사용되어서는 안된다. 예외는 잘못된 특별한 상황을 나타내야 하며, 처리되어야 한다.

---

하지만 null과 Failure는 예상되는 오류를 표현할 때 굉장히 좋다. 이는 효율적이며, 간단한 방법으로 처리할 수 있다.
충분히 예측할 수 있는 오류는 null과 Failure을 사용하고, 예측하기 어려운 예외적인 범위의 오류는 예외를 throw해서 처리하는 것이 좋다.

간단한 예를 보자.

```
// Null return하기
inline fun <refied T> String.readObjectOrNull(): T?{
	//...
    if(incorrectSign) {
    	return null
    }
    // ...
    retrun result
}

// Sealed Class이용하기
inline fun <refied T> String.readObjectObject(): Result<T>{
	//...
    if(incorrectSign) {
    	return Failure(JsonParsingException())
    }
    // ...
    retrun Success(result)
}

sealed class Result<out T>
class Success<out T>(val result: T): Result<T>
class Failure(val throwable: Throwable): Result<Nothing>()

class JsonParsingException: Exception()
```

null 과 Failure을 사용해서 다루는 오류는 다루기 쉬우며 놓치기 어렵다.
null을 처리해야한다면 사용자는 `안전호출(?)` 또는 `Elvis 연산자(?:)`와 같은 다양한 널 안전성 기능을 활용한다.

```
val age: String? = userText.readObjectOrNull<Person>()
```

또는 Result와 같은 `공용체(Union Type)`를 리턴하기로 했다면, when표현식을 사용해서 이를 처리할 수 있다.

```
val age = userText.readObjectOrNull<Person>()?.age ?: -1

val person = userText.readObjectOrNull<Person>()
val age = when(person){
	is Success -> person.age
    is Failure -> -1
}
```

이렇게 오류를 처리하면 try-catch블록보다 효율적이고 명확하게 처리할 수 있다.

예외를 throw한다면 전체 어플리케이션을 중지시킬 수도 있으며, null 값과 sealed result 클래스는 명시적으로 처리해야 하며, 어플리케이션의 흐름을 중지하지도 않는다.

#### null과 Failure을 사용하는 기준?

성공 및 실패에 대해 추가적인 정보가 필요한다면 sealed result를 사용하고, 그렇지 않으면 null을 사용하는 것이 일반적이다. `Failure는 처리할 때 필요한 정보를 가질 수 있다.`

---

### Sealed Class를 이용하여 retrofit2 결과 받아오기

```
sealed interface ApiResult<T : Any>

class ApiSuccess<T : Any>(val data: T) : ApiResult<T>
class ApiError<T : Any>(val code: Int, val message: String?) : ApiResult<T>
class ApiException<T : Any>(val e: Throwable) : ApiResult<T>
```

다음과 같이 Sealed Class를 정의하여 네트워크 결과를 `Success`, `Error`, `Exception`으로 나눈다.

```
suspend fun <T : Any> handleApi(
    execute: suspend () -> Response<T>
): NetworkResult<T> {
    return try {
        val response = execute()
        val body = response.body()
        if (response.isSuccessful && body != null) {
            ApiSuccess(body)
        } else {
            ApiError(code = response.code(), message = response.message())
        }
    } catch (e: HttpException) {
        ApiError(code = e.code(), message = e.message())
    } catch (e: Throwable) {
        ApiException(e)
    }
}
```

네트워크 Api의 결과를 handleApi라는 Extention을 정의하여 네트워킹 요청을 다룰 수 있다.

```
viewModelScope.launch {
    when (val response = repository.fetchData()) {
        is NetworkResult.Success -> posterFlow.emit(response.data)
        is NetworkResult.Error -> errorFlow.emit("${response.code} ${response.message}")
        is NetworkResult.Exception -> errorFlow.emit("${response.e.message}")
    }
}

```

오픈소스 라이브러리인 [Sandwich](https://github.com/skydoves/sandwich)를 사용하면 Retrofit 네트워크 응답에서 표준화 된 인터페이스를 구성해 준다.

```
disneyService.fetchDisneyPosterList().request { response ->
    response.onSuccess {
    	// ApiResponse.Success 일때 body data에 바로 접근 가능
    }.onError {
    	// ApiResponse.Failure.Error 일 때, message()를 이용해 errorBody에 접근가능
    }.onException {
    	// ApiResponse.Failure.Error or Exception 일때
    }
  }
```

코루틴에서의 네트워크 작업, 단위테스트, 에러 핸들링 등 여러 기능을 제공해준다.

참고 자료

https://heeeju4lov.tistory.com/34

https://proandroiddev.com/modeling-retrofit-responses-with-sealed-classes-and-coroutines-9d6302077dfe
