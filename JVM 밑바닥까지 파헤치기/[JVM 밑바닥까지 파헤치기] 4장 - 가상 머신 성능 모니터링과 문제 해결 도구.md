## 기본적인 문제 해결 도구

JDK의 `bin`디렉토리에는 다양한 도구가 있다. 그중 `java.exe`와 `javac.exe`부터, 그 외 도구들이 많지만 이 모두의 역할을 알 필요는 없다. (해당 도구들은 패키징, 배포, 서명, 디버깅, 모니터링, 운영, 유지 보수 등 다양한 상황에서 사용된다.)

이중 중요한 것 몇가지를 소개한다.

![](https://velog.velcdn.com/images/cksgodl/post/863b6c1e-06af-48ef-b6e5-d58818b601a8/image.png)

- javac (Java Compiler)
 Java 소스 코드를 컴파일하는 역할을 한다. 
 .java 파일을 받아서 이를 JVM이 이해할 수 있는 바이트코드인 .class 파일로 변환합니다.

- java (Java Application Launcher)
 컴파일된 바이트코드를 실행하는 역할을 합니다.

- JMC, JFR
  상용 인증 도구
  
등등 위의 도구들은 잘 살펴보면 대부분의 크기가 20KB이내이다. 이는 명령 줄 스크립트이며, 실제 동작하는 코드는 JDK 도구 라이버러리에 담겨져 있다.(`jmods`)  

### Jps

`JVM process status tool`인 `jps`가 있다. 동작 중신 가상 머신 프로세스 목록을 보여주며 각 프로세스에서 가상 머신이 실행한 메인 클래스(main() 메서드를 포함하는 클래스)의 이름을 알려준다.

```c
$ jps -l
7 app.jar
2523 sun.tools.jps.Jps

$ jps -v
2579 Jps -Dapplication.home=/usr/jdk64/jdk1.8.0_112 -Xms8m
7 jar -XX:InitialRAMPercentage=55 -XX:MinRAMPercentage=55 -XX:MaxRAMPercentage=55 -Dfile.encoding=UTF-8 -Dspring.profiles.active=beta -Duser.timezone=GMT+09
```

| 옵션  | 설명 |
|-------|------|
| `-q`  | 단순히 Java 프로세스 ID(PID)만 출력합니다. |
| `-m`  | 각 Java 프로세스가 시작될 때 전달된 메인 클래스나 JAR 파일 이름과 함께 전달된 인수를 출력합니다. |
| `-l`  | 각 Java 프로세스의 메인 클래스나 JAR 파일의 전체 패키지 이름을 출력합니다. |
| `-v`  | 각 Java 프로세스의 JVM 인수를 출력합니다. |
| `-J<flag>` | `jps` 명령 자체에 대한 JVM 인수를 전달합니다. 예: `-J-Xmx1024m` |
| `-mlv` | `-m`, `-l`, `-v` 옵션을 함께 사용하여 각 Java 프로세스의 메인 클래스나 JAR 파일 이름, JVM 인수, 시작 인수를 모두 출력합니다. |

### jstat

JVM 통계적 모니터링 도구(JVM stastics monitoring tool)인 jstat은 가상 머신의 다양한 작동 상태 정보를 모니터링하는 데 사용한다. 클래스 로딩, 메모리, 가비지 컬렉션, JIT컴파일과 같은 런타임 데이터를 보여 준다. 

__런타임 가상 머신 성능문제를 찾는 보편적인 도구로 활용될 수 있다.__

jstat 명령어 형식은 다음과 같다.

```c
jstat option vmid intervals count
```

- option : 질의할 가상 머신 정보 (클래스 로딩, 가비지 컬렉션, 런타임 컴파일 대상)
- vmid : java process id
- interval : 질의 간격
- count : 횟수

아래는 예제이다.

```c
$ jstat -gc 7 250 20
 S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC     YGCT    FGC    FGCT     GCT
 0.0   12288.0  0.0   12288.0 174080.0 112640.0  108544.0   87951.0   124416.0 123523.9 14272.0 13841.2    620    6.401   0      0.000    6.401
 ...
 0.0   12288.0  0.0   12288.0 174080.0 18432.0   108544.0   87953.5   124416.0 123523.9 14272.0 13841.2    621    6.407   0      0.000    6.407
 0.0   12288.0  0.0   12288.0 174080.0 18432.0   108544.0   87953.5   124416.0 123523.9 14272.0 13841.2    621    6.407   0      0.000    6.407
 
$ jstat -gccause 7 250 3
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT    LGCC                 GCC
     - 100.00  12.94  81.03  99.28  96.98    622    6.412     0    0.000    6.412 G1 Evacuation Pause  No GC
     - 100.00  12.94  81.03  99.28  96.98    622    6.412     0    0.000    6.412 G1 Evacuation Pause  No GC
     - 100.00  12.94  81.03  99.28  96.98    622    6.412     0    0.000    6.412 G1 Evacuation Pause  No GC
     
```
| 옵션  | 설명 |
|-------|------|
| `-class`  | 클래스 로드 및 언로드 통계를 출력합니다. |
| `-gc`     | 힙 메모리와 관련된 가비지 컬렉션 통계를 출력합니다. |
| `-gccapacity` | 각 영역의 힙 메모리 용량 통계를 출력합니다. |
| `-gcmetacapacity` | 메타스페이스 영역의 용량 통계를 출력합니다. |
| `-gcnew`  | 새로운 힙 영역의 가비지 컬렉션 통계를 출력합니다. |
| `-gcnewcapacity` | 새로운 힙 영역의 용량 통계를 출력합니다. |
| `-gcold`  | 오래된 힙 영역의 가비지 컬렉션 통계를 출력합니다. |
| `-gcoldcapacity` | 오래된 힙 영역의 용량 통계를 출력합니다. |
| `-gcutil` | 가비지 컬렉션과 관련된 힙 메모리 사용률 통계를 출력합니다. |
| `-gccause` | 가비지 컬렉션 통계와 GC 발생 원인을 출력합니다. |
| `-compiler` | JIT(Just-In-Time) 컴파일러 통계를 출력합니다. |
| `-printcompilation` | 최근에 JIT(Just-In-Time) 컴파일된 메서드에 대한 정보를 출력합니다. |

책에서 나온 예제는 아래와 같다.

```c
$ jstat -gcutil 7
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
     - 100.00  73.21  55.54  99.06  95.07  13231 1900.017     0    0.000 1900.017
```

| 요소  | 설명                                              | 예시 값  | 
|-------|---------------------------------------------------|----------|
| S0    | 첫 번째 서바이버 스페이스의 사용률(%)              | -        |
| S1    | 두 번째 서바이버 스페이스의 사용률(%)              | 100.00   |
| E     | 에덴 스페이스의 사용률(%)                         | 73.21    |
| O     | 올드 제너레이션의 사용률(%)                       | 55.54    |
| M     | 메타스페이스의 사용률(%)                          | 99.06    |
| CCS   | 압축 클래스 스페이스의 사용률(%)                  | 95.07    |
| YGC   | 젊은 세대에서 발생한 가비지 컬렉션의 횟수        | 13231    |
| YGCT  | 젊은 세대의 가비지 컬렉션에 소요된 총 시간(초)   | 1900.017 |
| FGC   | 전체 힙에 대한 가비지 컬렉션의 횟수              | 0        |
| FGCT  | 전체 힙에 대한 가비지 컬렉션에 소요된 총 시간(초)| 0.000    |
| GCT   | 가비지 컬렉션에 소요된 총 시간(초)                | 1900.017 |

- 에덴 공간을 73%, 생존자 공간을 100%, 구세대공간을 55% 사용하고 있다.
- 메타스페이스 사용률은 99%이다.
- 신세대 GC는 13000번 실행됬으며, 걸린시간은 총 1900초이다?!
- 전체 힙에 대한 가비지 컬렉션을 일어나지 않았다.

위의 상황을 이해하고 GC튜닝을 진행할 수 있을 것이다.

### jinfo

가상 머신의 다양한 매개 변수를 실시간으로 확인하고 변경하는 도구이다.

명령어 형식은 다음과 같다.

```c
jinfo option vmid
```

| 옵션        | 설명                                       | 사용 예시                      |
|-------------|------------------------------------------|--------------------------------|
| `-flags`    | JVM의 모든 플래그 값을 출력                       | `jinfo -flags <pid>`           |
| `-sysprops` | 시스템 속성을 출력                             | `jinfo -sysprops <pid>`        |
| `-help`     | 도움말 출력                                   | `jinfo -help`                  |


예제는 아래와 같다.


```
$ jinfo -flag ConcGCThreads 7
-XX:ConcGCThreads=1

$ jinfo -flag MaxHeapSize 7
-XX:MaxHeapSize=3544186880
```

### jmap

힙 스냅숏을 파일로 덤프해 주는 자바용 메모리 맵 명령어이다. 힙 스냅숏을 파일로 덤프함으로 충분한 파일 공간 및 메모리 사용량이 유지되어야 한다. 힙 스냅숏 덤프 외에도 jmap으로 F-큐, 자바 힙과 메서드 영역 상세 정보(사용량), 적용중인 컬렉터도 알아낼 수 있다.

> `jmap`을 사용하지 않고도 자바 힙을 덤프하는 방법이 몇 가지 더 있기는 하다. 
>
> 바로 `-XX;+HeapDumpOnOutOfMemoryError`옵션인데, 이를 사용하면 메모리ㅏㄱ 오버플로될 떄 가상 머신이 자동으로 힙을 덤프해 준다.


jmap의 옵션은 다음과 같다.

```c
jamp option vmid
```

| 옵션             | 설명                                                                 | 사용 예시                           |
|------------------|----------------------------------------------------------------------|-------------------------------------|
| `-heap`          | 힙 메모리의 사용 상태와 관련된 정보를 출력                           | `jmap -heap <pid>`                  |
| `-histo[:live]`  | 힙의 클래스 히스토그램을 출력 (선택적으로 살아있는 객체만 표시)        | `jmap -histo <pid>`                 |
| `-finalizerinfo` | f-큐 내부의 정보와 관련된 정보를 출력                                    | `jmap -finalizerinfo <pid>`         |
| `-lockstat`      | JVM에서의 모든 스레드의 모니터 락 정보를 출력                        | `jmap -lockstat <pid>`              |
| `-dump:file=<file>` | 힙 덤프를 지정한 파일로 저장                                       | `jmap -dump:format=b,file=heapdump.hprof <pid>` |
| `-dump:format=b,file=<file>` | 힙 덤프를 지정한 파일로 저장, 바이트 형식                           | `jmap -dump:format=b,file=heapdump.hprof <pid>` |
| `-dump:format=s,file=<file>` | 힙 덤프를 지정한 파일로 저장, SAMS 형식                           | `jmap -dump:format=s,file=heapdump.hprof <pid>` |


### jhat

가상 머신 힙 덤프 스냅숏 분석 도구이다. `jmap`으로 분석한 힙 스냅숏을 분석할 수 있다. 하지만 이를 활용하는 사람은 많지 않다. 

- 힙 스냅숏을 어플맄에ㅣ션이 배포된 서버에서 직접 분석하는 일은 거의 없다.
- jhat의 분석 기능은 단순하다.

따라서 외부 분석 도구나 온라인 분석 사이트를 활용할 것을 권장한다.

- Online GC Analyazer (무료 플랜을 가짐)
   - GC Log Analyzer
      https://gceasy.io/gc-index.jsp#features
   - GCViewer
   - GCEasy
   
### jstack

스레드 스냅숏을 생성하는데 쓰인다. (스레드 덤프 또는 자바 코어 파일이라고 부른다.)

jstack의 명령어 형식은 다음과 같다.

```c
jstack options vmid
```

---

이외에도 여러 자바 도구가 있지만, JVM상태를 모니터링하기 위한 도구들은 위의 명령어로만으로도 충분하다.

## GUI 도구

- JHSDB
- JConsole
- VisualVM
- BTrace
- JMC
- JITWatch

등 JVM을 모니터링하고 운영하기 위한 여러 GUI도구가 있다. 책에서는 해당 도구에 대한 사용법을 모두 설명하지만 모두 다 알필요는 없음으로 생략한다.



