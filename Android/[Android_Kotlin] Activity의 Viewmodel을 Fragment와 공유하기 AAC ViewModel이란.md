들어가기 전에 개념적으로 알아야 할 것이 있다.

## AAC ViewModel과 MVVM ViewModel
**ACC : Android Architecture Component**

> Q. MVVM에서의 ViewModel과 ACC에서 제공하는 ViewModel은 서로 다른가?

정답은 Yes라고 하기도 애매하다. 왜냐하면 두 ViewModel의 개념 자체가 다르기 때문이다.

#### MVVM ViewModel

* **MVVM의 뷰모델은 뷰와 모델 사이에서 데이터를 관리하고 바인딩해주는 역할이다.**

![](https://velog.velcdn.com/images/cksgodl/post/13a24524-83d5-4239-8d09-37dbbbda0009/image.png)

MVVM 패턴에서의 ViewModel은 View에 연결될 데이터와 메서드를 구현하고, 상태가 변화하게 되면 변경 알림 이벤트를 통해 View에게 상태 변화를 알려줍니다. View는 ViewModel의 상태 변화를 옵저빙 합니다.

이처럼 View와 Model의 중간에서 Data를 바인딩하거나 Model을 업데이트하는 구조를 MVVM ViewModel 이라고 한다.

 이는 비즈니스 로직과 프레젠테이션 로직을 UI로부터 분리하는 것을 목표로 하며 비즈니스 로직과 프레젠테이션 로직을 UI로부터 분리하게 되면 테스트, 유지 보수 측면에서 용이하다.

_Android에서만 사용하는 것이 아니라 다른플랫폼에서도 사용되는 디자인 모델이다._

#### ACC ViewModel

AAC에서의 ViewModel은 Android의 수명 주기를 고려하여 UI 관련 데이터를 저장하고 관리하도록 설계되는 것

**즉 [Android Developer : ViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel)의 설명 자체가 ACC ViewModel에 관한 설명이다.**

AAC ViewModel을 사용하면 기존의 Activity가 생명 주기 때문에 데이터 관리 측면에서 겪던 어려움들을 간단하게 처리할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/3d0ebd40-8471-4a09-aaae-b5e1f359e57e/image.png)


### 뭐가 다른데?

MVVM ViewModel은 View에 필요한 데이터를 관리하여 바인딩 해주고, 비즈니스 로직을 담당해 데이터를 처리하는 요소이고
AAC의 ViewModel은 Android의 수명 주기를 고려하여 UI 관련 데이터를 저장하고 관리하는 요소로 요약할 수 있다.

ACC ViewModel안에 MVVM ViewModel 포함된다고 생각하면 될 것 같다.
왜냐하면 AAC의 ViewModel로 MVVM 패턴의 ViewModel을 구현할 수 있기 때문이다. MVVM 패턴의 ViewModel의 역할은 위에서 보았듯이 View에 필요한 데이터를 관리하여 바인딩해주는 것이며, AAC의 ViewModel을 위의 개념대로 구현해주면 된다. ViewModel 내에서 ObservableField나 LiveData 등을 사용하여 데이터 바인딩 해준다면 MVVM 패턴의 ViewModel로써 사용이 가능하다.

[출처 : 꾸준하게](https://leveloper.tistory.com/216)

 ---
 
 ## Activity내에서의 View모델을 Fragment와 공유하기
 
 안드로이드는 AAC-ViewModel을 제공하는데 기본 3가지를 제공한다.

1. Activity에서 만 사용하는 경우
2. Fragment에서 만 사용하는 경우
3. **Activity를 기준으로 Fragment에서 공유해서 사용해야 할 경우**

1번과 2번같은 경우는 보통의 ACC-ViewModel을 구현하듯이 사용하면 된다. 이는 자기 자신(프래그먼트, 액티비티)의 LifeCycle을 따른다.

```
//Activity내에서의 ViewModel 선언
private lateinit var signupViewModel: SignupViewModel

override fun initView() {
        signupViewModel = ViewModelProvider(this).get(SignupViewModel::class.java)
        binding.lifecycleOwner = this
        binding.signupViewModel = signupViewModel		        
}
```

** 3 번의 경우 같은 ViewModel을 서로 다른 Acitivity와 Fragment에 선언하여 사용하면 되지않을까??**

![](https://velog.velcdn.com/images/cksgodl/post/cb15b21c-4ce0-4ac0-b9f1-55b00a0f2bdd/image.png)

Signup Activity와 그 내부의 Viewpager Fragment에서 같은 ViewModel을 선언하여 서로 데이터를 공유하는 것을 생각했다.

```
/Activity내에서의 ViewModel 선언
private lateinit var signupViewModel: SignupViewModel

override fun initView() {
        signupViewModel = ViewModelProvider(this).get(SignupViewModel::class.java)
        ...
}
```

```
//Fragment내에서의 Viewmodel 선언
private lateinit var signupViewModel: SignupViewModel

override fun initView() {
        signupViewModel = ViewModelProvider(this.get(SignupViewModel::class.java)
        binding.signupViewModel = signupViewModel
  	    ...
}

```

![](https://velog.velcdn.com/images/cksgodl/post/9f77089a-3569-4d4a-b9e6-ce388f7c6ffd/image.png)

그러나 실제로는 각각 ViewModel은 따로 생성되고 의존성은 존재하지 않는다.

이를 해결하기위해 사용하는 것이
[프래그먼트 간 데이터 공유 즉 SharedViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel?hl=ko)이다.

```
//In Android Developer
class SharedViewModel : ViewModel() {
    val selected = MutableLiveData<Item>()

    fun select(item: Item) {
        selected.value = item
    }
}

class ListFragment : Fragment() {
    private lateinit var itemSelector: Selector

    // Use the 'by activityViewModels()' Kotlin property delegate
    // from the fragment-ktx artifact
    private val model: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        itemSelector.setOnClickListener { item ->
            // Update the UI
        }
    }
}

class DetailFragment : Fragment() {

    // Use the 'by activityViewModels()' Kotlin property delegate
    // from the fragment-ktx artifact
    private val model: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        model.selected.observe(viewLifecycleOwner, Observer<Item> { item ->
            // Update the UI
        })
    }
}
```

 // Use the 'by activityViewModels()' Kotlin property delegate
    // from the fragment-ktx artifact

그러나 fragment-ktx artifact를 활용하라고 적혀있다.

```
// fragment-ktx 활용
private val activityViewModel: MainViewModel by activityViewModels {
    object : ViewModelProvider.Factory {
        override fun <T : ViewModel?> create(modelClass: Class<T>): T =
            MainViewModel() as T
    }
}
```

그러나 이를 활용하지 않고도
액티비티에서 초기화하고, Fragment에서 당겨다 쓰는 방법이 있다.

**ViewModelStoreOwner를** 변경해주면 된다.

Fragment이기 때문에 Fragment ViewModelStoreOwner를 활용하지 않고, Activity의 ViewModelStoreOwner를 활용하여 이미 생성된 Activity의 ViewModel을 활용할 수 있다.

```
    private val signupViewModel: SignupViewModel by lazy {
        ViewModelProvider(requireActivity(), object : ViewModelProvider.Factory {
            override fun <T : ViewModel?> create(modelClass: Class<T>): T =
                SignupViewModel() as T
        }).get(SignupViewModel::class.java)
    }
```

```
    private lateinit var signupViewModel: SignupViewModel 

    override fun initView() {
        signupViewModel = ViewModelProvider(requireActivity()).get(SignupViewModel::class.java)
        binding.signupViewModel = signupViewModel
}
```

이를 통해 
```
// InFragment 
// Nextbt이 눌렸을 때 ViewModel Data update
binding.signupNextBt.setOnClickListener{
            signupViewModel.setemail(binding.loginSignupEmailEdittv.text.toString())
            signupViewModel.setpasswrod(binding.loginSignupPasswdEdittv.text.toString())
}

// InActivity
// intent에 ViewModel의 값 집어 넣기
val intent = Intent(this, MainActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            intent.putExtra("Email",signupViewModel.email.value.toString())
            intent.putExtra("Password",signupViewModel.password.value.toString())
            startActivity(intent)

```

![](https://velog.velcdn.com/images/cksgodl/post/0e31dd18-3f7a-4715-86f3-1f6ec43ef77c/image.png)

Activity의 Viewmodel의 값을 Fragment에서 업데이트하여 Intent로 보내도 
잘 작동하는 것을 확인할 수 있다.

>Fragment의 ChildFragment 간에 ViewModel을 공유하는 방법(Activity ViewModel을 활용 X)
[출처 : Android Fragment 간의 ViewModel 공유하기](https://thdev.tech/androiddev/2020/07/13/Android-Fragment-ViewModel-Example/)


[예제 Github](https://github.com/dlgocks1/ALife_Android)
