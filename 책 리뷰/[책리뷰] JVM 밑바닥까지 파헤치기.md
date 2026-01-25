![](https://velog.velcdn.com/images/cksgodl/post/f1945eee-cb9b-4906-9f12-7557e596c526/image.png)

##  「JVM 밑바닥까지 파헤치기」 리뷰

 JVM의 내부 구조와 동작 원리를 딥하게 알려주는 책이다. 자바 바이트코드, 메모리 관리, GC, JIT 컴파일러, 동시성 활용법 등 JVM의 핵심을 체계적으로 설명하고, 관련 예제를 제공한다.
 
 해당 책의 내용을 실무에서도 이해하여 적용하고, 써먹을 수 있다. 단, JDK 21이상의 내용은 잘 제공되지 않는다. 

![](https://velog.velcdn.com/images/cksgodl/post/c73842b0-9054-4cda-84be-d9ce4d94a22b/image.png)

_이렇게 까지 깊게 알고 싶지는 않은데.. 너 자세하게 알려준다._

### 읽은 기간

1장에 1주씩 총 15주를 읽었다. (중간에 몇번 쉼) 1장을 1주에 읽기 어려운 내용도 있어 기간을 넉넉하게 잡기를 추천한다.


### 이런 사람에게 추천

- 운영 환경에서 성능 이슈를 직접 해결해야 하는 백엔드 개발자
- GC 튜닝, 메모리 누수 분석이 필요한 분
- "왜 그렇게 동작하는지" 원리가 궁금한 분

### 기억나는 책 내용들

#### JVM 내부 명령어

```kotlin
top -H -p <PID>

jps
jstack <PID> | grep "스레드명" -A 50
jmap
jstat
jinfo
```

실제로도 잘 활용했던 명령어

1. 무한 루프 쓰레드 탐지
2. 스레드 누수 탐지

#### G1GC 로그 분석

```kotlin
  -Xlog:gc*,gc+ergo*=trace,gc+age=trace:file=gc.log

  로그 해석 예시:
  GC(798) Pause Young (Normal) 4263M->591M(7424M) 10.693ms
           │                    │      │    │       └─ STW 시간
           │                    │      │    └─ 전체 힙
           │                    │      └─ GC 후
           │                    └─ GC 전
           └─ Young GC
```
  - Predicted base time: 10.55ms → 예상 GC 시간
  - Eden regions: 918->0 → Eden 영역 완전 수거
  - Survivor regions: 10->10 → Survivor 유지


#### 코드 캐시 확인

```kotlin
  jcmd <PID> Compiler.codecache

  CodeHeap 'non-profiled nmethods': used=39781Kb  ← C2 컴파일 코드 (83.5%)
  CodeHeap 'profiled nmethods': used=7860Kb       ← C1 컴파일 코드 (16.5%)
```

#### Integer 캐싱 함정

```kotlin
  Integer c = 3;
  Integer d = 3;
  Integer e = 321;
  Integer f = 321;

  c == d  // true  (-128~127은 캐싱)
  e == f  // false (321은 캐싱 범위 밖)
```

#### 원시 타입 vs 참조 타입 메모리

```kotlin
  // int 배열 vs Integer 리스트 = 6배 메모리 차이!
  val intArray: IntArray = intArrayOf(1, 2, 3)      // 원시 타입
  val intList: List<Int> = listOf(1, 2, 3)          // 박싱됨 (Integer)
```

#### 코루틴에서 synchronized 주의점

```kotlin
  // ❌ 위험 - suspend 함수 내에서 synchronized 사용
  suspend fun bad() = synchronized(lock) {
      delay(100)  // 컴파일 에러! suspend 중에도 락 유지됨
  }

  // ✅ 올바른 방법 - Mutex 사용
  private val mutex = Mutex()
  suspend fun good() = mutex.withLock {
      delay(100)  // OK - 코루틴 suspend 시 락 해제
  }
```

#### JIT 컴파일러 계층

```
  jstat -compiler <PID>
  # Compiled: 64857 (누적 컴파일 횟수)
 
 Level 0: 인터프리터
      ↓ (호출 횟수 증가)
  Level 1-3: C1 컴파일러 (빠른 컴파일, 기본 최적화)
      ↓ (핫스팟 감지)
  Level 4: C2 컴파일러 (느린 컴파일, 공격적 최적화)
```

Jit 컴파일 최적화와, Grall VM 최적화에 대하여
Jit JVM 설정 명령어들


#### 락 상태 변화 (Mark Word)

```
  Biased Lock → Thin Lock → Fat Lock
     (단일 스레드)  (CAS 경쟁)   (OS mutex)

  비용: ~0      비용: CAS     비용: 시스템콜
```


## 총평

  JVM 기반 언어를 사용하는 개발자라면 한 번쯤 읽어볼 가치가 있는 책이다. 특히 운영 환경에서 장애 대응이나 성능 최적화를 직접 해야 할 때, 이 책에서 배운
지식이 큰 도움이 되었다.

 하지만 지나친 TMI와 내용이 읽기가 힘들다. 전체적인 맥락 및 내용을 알고 읽으면 읽히지만, 무지하게 책부터 읽으면 별도로 따로 공부를 추가적으로 해야한다. 


평점: ⭐⭐⭐⭐ (4/5)