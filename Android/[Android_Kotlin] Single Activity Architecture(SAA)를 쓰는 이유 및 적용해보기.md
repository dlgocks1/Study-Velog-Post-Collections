### Android Jetpack
> Jetpack은 개발자가 관심 있는 코드에 집중할 수 있도록 권장사항 준수, 상용구 코드 축소, 모든 Android 버전 및 기기에서 일관되게 작동하는 코드 작성을 돕는 라이브러리 모음입니다.

안드로이드 앱을 더 완성도있게 만들 수 있는 라이브러리라고 생각하면 될 것 같다.

![](https://velog.velcdn.com/images/cksgodl/post/f4845972-3808-449c-9a58-85d3fb67eee3/image.png)

이러한 Jetpack에서 제공하는 것이 있는데 바로 navigation이다
* [navigation](https://developer.android.com/jetpack/androidx/releases/navigation)
인앱 UI를 빌드 및 구조화하고 딥 링크를 처리하며 화면 간에 이동합니다.

navigation 모듈을 활용하면

앱 내 프래그먼트끼리의 이동을 도와주며, view들이 시각적으로 어떻게 연결되어 있는지 알수 있고, 수정을 쉽게 만들어 준다.

![](https://velog.velcdn.com/images/cksgodl/post/b5b8e198-7e3a-4229-aa2a-f8c51b7117c9/image.png)

또한 SAA 구현하기 쉽게 만들어 준다고 한다.
그렇다면 SAA의 장점은 무엇일까?

### Single Activity Architecture

SAA는 하나의 또는 적은 activity로 앱을 구성하는 것을 의미한다. 

[10 best practices for moving to a single activity
](https://www.youtube.com/watch?v=9O1D_Ytk0xg)


왜 Activity를 하나만 사용할까?

1. Activity는 Fragment에 비하여 상대적으로 무겁기 때문에 메모리나 속도 방면에서 Fragment를 사용하는 것이 이득이다.

2. 비즈니스 로직을 Fragment 단위로 분리하여 사용 가능, Activity보다 유연한 UI 디자인을 지원한다.

3. activity Scope 내에서 Shared ViewModel을 사용하여 데이터를 공유 및 전달 할 수 있다.
한쪽 프래그먼트에서는 Data를 Update하고, 다른 한 프래그먼트에서는 Observing하여 view의 변화를 주는 것도 가능
![](https://velog.velcdn.com/images/cksgodl/post/7636736b-6b45-4a08-b48c-26cefe302489/image.png)

4. Intent, Acitivty Compat, StartActivity... 등 화면을 전환하는 여러 방법들을 Navigation을 사용하여 단순화 할 수 있다.
	+ type safe arguments를 fragment 사이에 전달 가능하다.
    + 테스트를 작성할 때에는 destination level이 아닌 뷰 모델에 대해 테스트를 작성 한다.
    + Testing Navigation : FragmentScenario 및 Navcontroller를 포함하고 있기 때문에 프래그먼트 사이의 connection을 테스팅 가능하다.
    

---

### 프로젝트에 적용시켜보기

Navigation Implements
```
    // Navigation
    implementation 'androidx.navigation:navigation-fragment-ktx:2.5.0'
    implementation 'androidx.navigation:navigation-ui-ktx:2.5.0'
    
    // Fragemnt Ktx
    implementation "androidx.fragment:fragment-ktx:1.5.0"
    
```

Safe Args (Project 단위 Gradle)

```
classpath "androidx.navigation:navigation-safe-args-gradle-plugin:2.5.1"

```

nav_garph.xml 만들기

내비게이션의 관련된 모든 정보를 가진 XML 파일을 만들어준다. 

res/navigation
![](https://velog.velcdn.com/images/cksgodl/post/aebe7be8-3cfe-4f21-9bbb-c1f2fa3f1f5f/image.png)

navigation의 태그로써는 
* navigation : navGraph의 기본태그, 타 nav garph도 include하여 사용할 수 있다.
* fragment, activity, Dialog 등 Destination
* action : 화면 이동에 대한 설정, 애니메이션 도착지 등등..
* argument : 전달한 파라미터 정의
* deeplink : 딥 링크에 대한 내용 -> URL Scheme과 비슷한 느낌


activity.xml 에서 FragmentContainerView 추가하기
```
<androidx.fragment.app.FragmentContainerView
            android:id="@+id/main_nav_host_fragment"
            android:name="androidx.navigation.fragment.NavHostFragment"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            app:defaultNavHost="true"
            app:navGraph="@navigation/clofit_nav_graph" />
```

activity.kt 에서 NavController 등록하기
```
    private lateinit var navController: NavController
    
    private fun setupJetpackNavigation() {
        val host = supportFragmentManager
            .findFragmentById(R.id.main_nav_host_fragment) as NavHostFragment? ?: return
        navController = host.navController
       
       // BottomNavigation 설정 
       binding.bottomNavigationView.setupWithNavController(navController)

		// BottomNavigation View 선택했을 때 해당뷰로 이동하게 하기
        // true를 반환하여 BottomNavigationView에서 선택한 item을 선택한 item으로 표시합니다.
        binding.bottomNavigationView.setOnItemSelectedListener { item ->
            // 예상된 동작을 얻으려면 default Navigation 메서드를 수동으로 호출해야 합니다.
            NavigationUI.onNavDestinationSelected(item, navController)
            return@setOnItemSelectedListener true
        }

    }

```

Bottom Navigation과 연결하기

activity.xml
```
 <com.google.android.material.bottomnavigation.BottomNavigationView
        android:id="@+id/bottom_navigation_view"
        android:layout_width="0dp"
        android:layout_height="56dp"
        android:background="@color/black_900"
        app:itemIconSize="18sp"
        app:itemIconTint="@drawable/menu_selector_color"
        app:itemTextColor="@drawable/menu_selector_color"
        app:labelVisibilityMode="unlabeled"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:menu="@menu/bottom_navigation_menu" />
```

중요한 점은 menu.xml에 등록한 ID와 nav_graph에 등록한 ID가 동일해야한다는 점이다.
```
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:id="@+id/fragment_home"
        android:title="@string/home"
        android:icon="@drawable/icon_bulb_unselected" />
     ...
</menu>

// nav_graph.xml
<fragment
	android:id="@+id/fragment_home"
	android:name="com.clofit.clofit.ui.view.main.MainFragment"
	android:label="@string/home">
```

[nested graph](https://developer.android.com/guide/navigation/navigation-nested-graphs?hl=ko)를 사용해 기존 Activity에서 사용하던 graph를 그대로 가져와 사용할 수 있다.

프래그먼트 이동하는 법은
만들어진 해당 뷰의 Directions객체를 참조하여 이동하고자 하는 action을 가져와서 사용한다.
```
val action = MypageFragmentDirections.actionFragmentMypageToGalleryFragment() // Argument 넣기
indNavController().navigate(action)
```

---

### Issue

>  #### Setting the fragment as the LifecycleOwner might cause memory leaks because views lives shorter than the Fragment. Consider using Fragment's view lifecycle


https://stackoverflow.com/questions/57647751/android-databinding-is-leaking-memory

만들어진 Fragment들에 대한 Databinding Lifecycle은 viewLifecyclerOwner로 설정해야 한다고 한다.

![](https://velog.velcdn.com/images/cksgodl/post/bad663f5-e7ff-47c4-a244-2fc523f138e0/image.png)

왜? Navigation으로 이동 중 백스택에 쌓인 Fragment는 onDestroyView()는 불렸지만 onDestoy()는 불리지 않음으로 메모리 누수가 발생할 수 있다고 한다. 이로 인해 fragment 자체를 생명주기로 두는 것 보다 좀 더 작은 생명주기는 viewLifeCyclerOwner를 생명주기로 두는 것이 안전하다고 하다. 

```
_binding?.lifecycleOwner = this.viewLifecycleOwner
```

---

#### 프래그먼트 이동 중 BottomNavigation 지우기

> Acitivity를 하나만 사용하는 과정 중에 BottomNavigation을 Global UI로 사용하고 있어 필요 없는 프래그먼트에도 뷰가 출력되는 문제가 발생하였다.

nav Controller에 DestinationChangedListener을 달아주어서 해당 도착지점이 바텀네비게이션이 필요없는 뷰라면 hide를 해주었다.


```
    private fun initDestinationListener() {
        navController.addOnDestinationChangedListener { _: NavController?, destination: NavDestination, _: Bundle? ->
            if (destination.id == R.id.galleryFragment) {
                hideBottomNavigation()
            } else {
                showBottomNavigation()
            }
        }
    }
```


참고 자료

https://heegs.tistory.com/128

https://jinyand.tistory.com/6

https://stackoverflow.com/questions/70763230/how-to-hide-bottom-bar-nav-when-following-single-activity-design

