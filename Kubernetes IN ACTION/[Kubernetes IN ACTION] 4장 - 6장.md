# 4장 레플리케이션과 그 밖의 컨트롤러: 관리되는 파드 배포하기

쿠버네티스위에 올린 파드는 어디선가 계속 실행되도록 보장된다.

파드가 노드에 스케줄링되는 즉시, 해당 노드의 `kubelet`은 파드의 컨테이너를 실행하고 파드가 존재하는 한 컨테이너가 계속 실행되도록 한다. 

컨테이너의 주 프로세스(ps : 1)에 크래쉬가 발생하면 `kubelet`이 컨테이너를 다시 실행한다. 어플리케이션이 버그가 있어 크래시가 발생해도 어플리케이션이 자동으로 재시작한다. 

__즉 쿠버네티스에서 어플리케이션을 실행하는 것만으로도 자동으로 치유할 수 있는 능력이 주어진다.__

그러나 어플리케이션이 `OOM`이 나서 크래시가 나진 않지만, 프로세스가 계속 실행될 수도 있다. 이를 방지하기 위해서 어플리케이션 외부 상태에 의존하지 않고 내부상태에 의존하는 방법이 있다.

## 라이브니스 프로브

쿠버네티스는 내부적으로 컨테이너가 살아있는지를 라이브니스 프보르(liveness probe)를 통해 확인할 수 있다.

- [컨테이너 프로브 - kubernertes.io](https://kubernetes.io/ko/docs/concepts/workloads/pods/pod-lifecycle/#%EC%BB%A8%ED%85%8C%EC%9D%B4%EB%84%88-%ED%94%84%EB%A1%9C%EB%B8%8C-probe)

쿠버네티스는 세 가지 메커니즘을 사용해 컨테이너에 프로브를 실행한다.

1. `exec`
컨테이너 내에서 지정된 명령어를 실행한다. 명령어가 상태 코드 0으로 종료되면 진단이 성공한 것으로 간주한다.

2. `httpGet`
지정한 포트 및 경로에서 컨테이너의 IP주소에 대한 HTTP GET 요청을 수행한다. 응답의 상태 코드가 200 이상 400 미만이면 진단이 성공한 것으로 간주한다.

3. `tcpSocket
지정된 포트에서 컨테이너의 IP주소에 대해 TCP 검사를 수행한다. 포트가 활성화되어 있다면 진단이 성공한 것으로 간주한다. 원격 시스템(컨테이너)가 연결을 연 이후 즉시 닫는다면, 이 또한 진단이 성공한 것으로 간주한다.

+) GRPCContainerProbe를 활용하면 아래 방법도 사용 가능하다.

4. `grpc`
gRPC를 사용하여 원격 프로시저 호출을 수행한다. 체크 대상이 gRPC 헬스 체크를 구현해야 한다. 응답의 status 가 SERVING 이면 진단이 성공했다고 간주한다. gRPC 프로브는 알파 기능이며 GRPCContainerProbe 기능 게이트를 활성화해야 사용할 수 있다.

### HTTP 기반 라이브니스 프로브

```yaml
# 기본 항목
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: liveness
  name: liveness-http

# Pod Spec
spec:
  # Container spec
  containers:
  - name: liveness
    image: k8s.gcr.io/liveness
    args:
    - /server
    livenessProbe:
      httpGet: # Http 리퀘스트 반환 값에 따라 체크함
        path: /healthz
        port: 8080
        httpHeaders:
        - name: X-Custom-Header
          value: Awesome
        initialDelaySeconds: 10 # 처음 감시할 때 까지의 Delay
        periodSeconds: 5 # Liveness Probe 실행 간격
```

8080파트의 `/healthz`를 검증한다. 이외에도 다음과 같은 설정을 지정할 수 있다.

- 초기 지연 시간
- 응답 제한 시간
- 기간 (period)

> 어플리케이션 초기 지연시간을 고려하여 이니셜딜레이 설정 -> 임계값을 초과하게 되면 컨테이너 재시작

`kubectl describe` 명령어를 통해 컨테이너 이벤트 및 다시시작 이유를 볼 수 있다.

```
Containers:
	...
    Limits:
      cpu:                8
      ephemeral-storage:  8Gi
      memory:             8Gi
      ncc/type.any:       1
    Requests:
      cpu:                100m
      ephemeral-storage:  8Gi
      memory:             1Gi
      ncc/type.any:       1
    Liveness:             http-get http://:prom-metrics/actuator/health delay=0s timeout=1s period=10s #success=1 #failure=3
    Readiness:            http-get http://:prom-metrics/actuator/health delay=0s timeout=1s period=10s #success=1 #failure=3
```

만약 문제가 발생한다면 종료 코드가 해당 설명에 노출되게 되며 이후 공부할 컨테이너훅을 활용해 이런 이벤트에 트리거를 달 수 있다.


### 효과적인 라이브니스 프로브를 위하여

- 프보르븝 가볍게 유지하라.
  - 웹서버가 백엔드 데이터베이스를 연결하지 못하는 경우에 실패를 반환해서는 안된다. 어플리케이션 외부이외의 내부만 체크하라
  - 라이브니스 프로브는 1초이내로 실행되어야 한다.
- 프로브에 재시도 로직을 구현하지 마라.
  - 어짜피 컨테이너가 재시작 된다.
  
  
## 레플리케이션컨트롤러에 대해

> __디플로이먼트와 레플리카셋__의 이전 버전이다. 개념만 알고 가기

이는 쿠버네티스 리소스로써 파드가 항상 실행되도록 보장한다. 선언된 상태에 따라 파드들을 유지시킨다.

![](https://velog.velcdn.com/images/cksgodl/post/a32ecf88-dfef-42ce-a001-0b433568fe2c/image.png)


이는 스펙에 선언된 `label`과 일치하는 파드들을 지속적으로 모니터링하고, 실제 파드 수와 일치하는지 주기적으로 확인한다.

- 이는 이전장(3장)에서 배웠던 레이블 설렉터를 활용한다.

### YAML 파일 구성 소개

이는 세 가지 요소로 구성된다.

```yaml
apiVersion: v1
kind: ReplicationController # 종류 선언
metadata:
  name: nginx
spec:
  replicas: 3 # 레플리카 수
  selector: # 레이블 설렉터
    app: nginx
  template: # 템플릿
    metadata:
      name: nginx
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
```

- 레이블 설렉터
   - 어떤 레이블들의 파드를 관리할 지 
- 레플리카 수
- 파드 템플릿
   - 뛰울 포드의 디테일을 설정

아래 명렁어를 통해 레플리케이션 컨트롤러를 생성한다.

```c
./kubectl creat -f kubia-rc.yaml
```

파드가 종료될 때 레플리케이션을 이를 다시 시작하는건 당연하다. 하지만 레플리케이션 컨트롤러는 노드가 죵료되어 파드가 실패했을 때도 다른 노드에 파드를 또 뛰운다. 시스템이 자동으로 스스로 치유한다. 

- 참고) 한 파드의 레이블을 수동으로 변경하면 레플리케이션컨트롤러는 이를 감지하고 새로운 파드를 다시 뛰운다. 
별도의 레이블을 추가하는 것은 아무런 의미가 없다. (레이블 설렉터에 의해 관리되는 것은 동일하기 때문에)

#### 파드 스펙(템플릿) 변경

레플리케이션의 파드 스펙을 변경하여도 기존 파드들엔 영향이 없다. 따라서 기존 파드를 모두 삭제하고 새로 뛰어야 한다.

이런 파드 스펙이나 레플리카 수를 변경할 떄는

```c
./kubectl eidt rc <이름>
```

명령어를 통해 텍스트 편집기를 열고, 해당 `yaml`을 수정한다.

레플리케이션컨트롤러를 삯제해도 파드는 그대로 유지된다. 따라서 이를 같이 삭제하기 위해서는 `cascade`옵션을 활용할 수 있다.

```c
./kubectl delete rc kubia --cascade=false
```

## 레플리케이션컨트롤러 대신 레플리카셋 사용하기

> 이는 차세대 레플리케이션 컨트롤러며 레플리케이션컨트롤러를 완전히 대체한다.

#### 이는 더 풍부한 파드 설렉터를 가진다.
  - 다양한 레이블 매칭
  - 레이블 키의 존재만으로 파드 매칭

메니페스틑 레플리케이션 컨트롤러와 비슷하다. (apiVersion, kind, 라벨 설렉터만 다름0

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend
  labels:
    app: guestbook
    tier: frontend
spec:
  # 케이스에 따라 레플리카를 수정한다.
  replicas: 3
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - name: php-redis
        image: gcr.io/google_samples/gb-frontend:v3

```


## 데몬셋을 활용해 각 노드에서 정확히 한 개의 파드 실행하기

레플리카셋, 디플로이먼트는 쿠버네티스 클러스터 내 어딘가에 지정된 수만큼의 파드를 실행하는 데 사용된다. 그러나 클러스터의 모든 노드에, 노드당 하나의 파드만 실행되길 원하는 경우 **데몬셋**을 활용할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/33ce64b0-c02e-47d2-b785-493af51cc664/image.png)

시스템 수준의 인프라 관련 파드가 좋은 예이다.(`kube-proxy` 등)

- 이 또한 노드 설렉터를 통해 특정 노드에서만 생성되도록 할수 있다.

> 노드의 레이블삭제 및 수정에 따른 데몬셋의 행동은 레플리카셋과 동일하게 작동한다.


## 완료 가능한 단일 테스크를 수행하는 파드 실행하기

특정 작업을 완료하고 종료되는 테스크를 실행할 수 있다. 이를 __잡__이라고 한다.

### 잡 리소스 소개

쿠버네티스는 잡 리소스를 지원하며 이는 프로세스가 성공적으로 완료되면 컨테이너를 다시 시작하지 않는 파드를 실행할 수 있다. 이때 파드는 완료된 것으로 간주된다.

- 노드에 장애가 발생할 경우 이는 다른 노드로 스케줄링 된다.

### yaml

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl:5.34.0
        command: ["perl",  "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4
```

_예시는 파이(π)의 2000 자리까지 계산해서 출력한다. 이를 완료하는 데 약 10초가 소요된다._

`restartPolicy`을 `OnFailure` 또는 `Never`로 명시적으로 설정하여 관리해야한다. (컨테이너가 종료 후에 재시작 되지 않아야 하기 때문에)


### 잡의 병렬성

또한 잡은 두 개 이상의 파드 인스턴스를 생성해 병렬 또는 순차적으로 실행할 수 있도록 구성할 수 있다.

`completions`와 `parallelism`속성을 설정해 수행한다.

- `completions : 5` : 다섯개의 파드를 순차적으로 완료될때까지 수행한다.

- `parallelism  : 2` : 잡을 동시에 병렬로 실행시킨다.


#### 잡 파드가 완료되지 않는다면

컨테이너의 프로세스가 무한루프를 도는 등 종료되지않는다면 `activeDeadlineSeconds`속성을 설정해 파드의 실행 시간을 제한할 수 있다.


## 크론 잡

> 쿠버네티스는 일정간격으로 반복 실행하는 잡 리소스를 제공한다.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "* * * * *"
  startingDeadlineSeconds: 15 # 파드는 예정된 시간 내에서 늦어도 15초 이내 시작되어야 한다.
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox:1.28
            imagePullPolicy: IfNotPresent
            command:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure
```

크론 잡은 생성이 되지 않거나, 동시에 두 이상 생성될 수도 있다. 따라서 잡이 수행하는 작업은 멱등성을 가져야 한다.

## 요약

- 컨테이너가 더 이상 정상적이지 않으면 즉시 쿠버네티스가 컨테이너를 다시 시작하도록 라이브니스 프로브를 지정할 수 있다.
- 파드는 실수로 삭제되거나 실행 중인 노드에 장애가 발생하거나 노드에서 퇴출되면 다시 생성되지 않기 때문에 파드를 직접 생성하면 안된다.
- 레플리케이션컨트롤러 or 레플리카셋은 선언된 상태에 따라 복제본의 수를 유지한다.
  - 템플릿을 변경해도 기존 파드에는 영향이 가지 않는다
  - 레플리카 수를 변경하면 영향이 간다.
- 데몬 셋은 노드마다 하나의 인스턴스가 실행되도록 한다.
- 배치작업은 잡 리소스로 생성해야 한다. (디플로이먼트나 오브젝트로 생성 X)
- 언젠가 실행해야 하는 잡은 크론잡 리소스를 통해 생성할 수 있다.


# 5장 서비스: 클라이언트가 파드를 검색하고 통신을 가능하게 하는 리소스

- 파드의 IP는 클러스터 내부에서는 접근이 가능하지만 외부에는 노출되지 않는다.
- 파드는 일시적이다. 즉, IP가 바뀐다.
- 클라이언트는 서버의 파드 IP주소를 미리알 수 없다.
- 모든 파드(레플리카 셋)에 동일한 IP주소로 접근이 가능해야 한다.

이러한 문제점을 해결하기 위해 쿠버네티스는 서비스를 제공한다.

## 서비스 소개

> 서비스는 생성될 떄 절대 바뀌지 않는 IP주소와 포트를 가지고 있다. 해당 IP주소와 포트를 활용해 특정 포드 중 하나로 연결할 수 있다.


![](https://velog.velcdn.com/images/cksgodl/post/ceb3f44f-85ba-4525-941e-deba2634daec/image.png)

서비스는 레플리카셋과 동일하게 레이블 설렉터를 활용해 동일한 세트에 속하는 파드를 지정하여 연결해준다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP		# 생략 가능
  selector:
    app.kubernetes.io/name: MyApp
  ports:
    - protocol: TCP
      port: 80 # 포트 80은 파드의 포트 9376과 매핑된다.)
      targetPort: 9376
```


- 쿠버네티스는 여러 포트를 지원할 수 있다. (굳이 두개의 서비스를 만들 필요가 없다.)

- 이러한 서비스 포트내용은 컨테이너의 환경 변수로 저장된다.

```c
./kubectl exec <파드 이름> env

....
XMS=4g
XMX=6g
TZ=Asia/Seoul
SPRING_PROFILES_ACTIVE=beta
SERVICE_HOST=
SERVICE_PORT=
```

- 서비스 IP에 핑을 할 수는 없다.(서비스의 클러스터 IP가 가상IP임으로)

### 서비스 퍼블리싱

쿠버네티스 `ServiceTypes`는 원하는 서비스 종류를 지정할 수 있도록 해 준다. Type 값과 그 동작은 다음과 같다.

- ClusterIP: 서비스를 클러스터-내부 IP에 노출시킨다. 이 값을 선택하면 클러스터 내에서만 서비스에 도달할 수 있다. 이것은 서비스의 type을 명시적으로 지정하지 않았을 때의 기본값이다.
- NodePort: 고정 포트 (NodePort)로 각 노드의 IP에 서비스를 노출시킨다. 노드 포트를 사용할 수 있도록 하기 위해, 쿠버네티스는 type: ClusterIP인 서비스를 요청했을 때와 마찬가지로 클러스터 IP 주소를 구성한다.
- LoadBalancer: 클라우드 공급자의 로드 밸런서를 사용하여 서비스를 외부에 노출시킨다.
- ExternalName: 값과 함께 CNAME 레코드를 리턴하여, 서비스를 externalName 필드의 내용(예:foo.bar.example.com)에 매핑한다. 어떠한 종류의 프록시도 설정되지 않는다.

[쿠버네티스 서비스 유형](https://seongjin.me/kubernetes-service-types/)참고하기

# 인그레스에 관하여

이는 외부에서 쿠버네티스에 접속할 수 있는 또 다른 방법이다.

## 인그레스가 필요한 이유

로드밸런서 서비스는 자신의 공용 IP주소를 가진 로드밸런서가 필요하지만, 인그레스는 한 IP주소로 수십 개의 서비스에 접근이 가능하도록 지원해준다.

즉 클라이언트가 HTTP요청을 인그레스에 보낼 때, 요청한 호스트와 경로에 따라 요청을 전달할 서비스가 결정된다.

![](https://velog.velcdn.com/images/cksgodl/post/77d4f232-11ee-4dac-b717-1088f4d3a40c/image.png)

인그레스는 네트워크 계층의 어플리케이션 계층에서 작동하며 서비스가 할수 없는 쿠키 기반 로드밸런서등의 기능을 제공한다.




```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-wildcard-host
spec:
  rules:
  - host: "foo.bar.com"
    http:
      paths:
      - pathType: Prefix
        path: "/bar"
        backend:
          service:
            name: service1
            port:
              number: 80
  - host: "*.foo.com"
    http:
      paths:
      - pathType: Prefix
        path: "/foo"
        backend:
          service:
            name: service2
            port:
              number: 80
```

위의 예시와 같이 와일드 카드도 사용 가능하고, 여러 호스트와 경로를 여러 서비스에 매핑할 수 있다.

예를 들면 다음과 같다.

- 동일한 호스트의 다른 경로로 여러 서비스 매핑
- 서로 다른 호스트로 서로 다른 서비스 매핑

또한 TLS 트래픽을 처리하여 `https`를 인그레스에서 제공할 수 있다.


## 레디니스 프로브

라이브니스 프로브는 불안전한 컨테이너를 자동으로 다시 시작해 어플리케이션을 구동하는 것을 의미한다.

레디니스프로브는 특정 파드가 클라이언트 요청을 수신할 수 있는지를 결정한다. 컨테이너가 레디니스 프로브를 성공한다면, 컨테이너가 요청을 수락할 준비가 되었음을 의미하며 인그레스 연결이 진행된다.

### 레디니스 프로브 유형

라이프니스 프로브와 동일하게 세 가지 유형이 있다.

- 프로세스를 실행하는 Exec 프로브 -> 컨테이너의 상태를 프로세스의 종료 상태 코드로 결정
- HTTP GET 프로브
- TCP소켓 프로브 : TCP 소켓이 연결되면 컨테이너가 준비된 것으로 간주


레디니스 프로브는 점검에 실패하더라도 컨테이너가 종료되거나 다시 시작되지 않는다. 점검이 완료된 파드만 요청을 수신하도록 한다. 이는 컨테이너를 시작할 때 주로 필요하지만, 컨테이너가 작동한 후에도 유용하다.

> 레디니스 프로브에서 실패한 파드는 엔드포인트 오브텍트에서 제거된다. 서비스가 연결되어 있다면 요청은 파드로 전달되지 않는다.

### 레디니스 프로브는 항상 정의하라

파드에 레디니스 프로브를 추가하지 않으면 파드가 시작하는 즉시 서비스 엔드포인트가 된다.

즉 `Connection refused` 클라이언트 에러를 피하기 위해서는 레디니스 프로브를 정의하라.

## 서비스 문제 해결

서비스는 쿠버네티스에서 가장 많이 사용되는 리소스이며 개발자가 좌절하는 부분이기도 하다. 다음은 서비스의 문제점과 해결방법을 간단하게 정리했다.

- 외부가 아닌 클러스터 내에서 서비스의 클러스터 IP에 연결되는지 확인할 것
- 서비스에 액세스할 수 있는지 확인하려고 서비스 IP로 핑을 할 필요가 없다.(서비스의 클러스터 IP는 가상IP임으로 핑되지 않음)
- 레디니스 프로브를 정의했다면 성공했는지 확인하라.
- 파드가 서비스의 일부인지 확인하려면 `kubectl get endpoints`를 활용하라
- 대상 포트가 아닌 서비스로 노출된 포트로 연결하고 있는지 확인하라
- 파드 IP에 직접 연결해 파드가 올바른 포트에 연결돼 있는지 확인하라.
- 파드 IP로 애플리케이션에 액세스할 수 없는 경우 어플리케이션이 로컬호스트에만 바인딩하고 있는지 확인하라.

## 요약

- 서비스는 단일 IP주소와 포트로 특정 레이블 설렉터와 일치하는 여러 개의 파드를 노출한다.
- 기본적으로 클러스터 내부에서 서비스에 액세스할 수 있지만, 유형을 노드포트 또는 로드밸런서로 설정해 클러스터 외부에서 서비스에 액세스할 수 있다.
- **파드가 환경변수를 검색해 IP주소와 포트로 서비스를 검색할 수 있다.**
- 관련된 어플리케이션 리소스를 만드는 대신 설렉터 설정 없이 서비스 리소스를 생성해 클러스터 외부에 있는 서비스를 검색하고 통신할 수 있다.
- EnternalName 서비스 유형으로 외부 서비스에 대한 DNS CNAME 별칭을 제공한다.
- 단일 인그레스로 여러 HTTP 서비스를 노출한다.
- 파드 컨테이너의 레디니스 프로브는 파드를 서비스 엔드포인트에 포함해야 하는지 여부를 결정한다.
- 헤드리스 서비스를 생성하면 DNS로 파드 IP를 검색할 수 있다.

# 6장 볼륨: 컨테이너에 디스크 스토리지 연결

컨테이너가 어떻게 외부 디스크 스토리지에 접근하는지, 어떻게 컨테이너 간에 스토리지를 공유하는지 살펴보자.

파드는 내부에 프로세스가 실행되고 CPU, RAM, 네트워크 인터페이스 등의 리소스를 공유한 논리적 호스트와 유사하다. 

> 파드 내부의 각 컨테이너는 고유하게 분리된 파일시스템을 가진다. 파일시스템은 컨테이너 이미지에서 제공되기 때문이다.


- 새로운 컨테이너가 시작하면 컨테이너 이미지를 빌드할 떄 추가한 파일들을 갖는 컨테이너를 시작한다.
   - 새로운 컨테이너는 이전에 실행했떤 컨테이너에 쓰여진 파일시스템의 어떤것 도 볼 수 없다.
   
파일시스템이 보존되기를 원할 수 있다. **쿠버네티스는 스토리지 볼륨을 정의하는 방법으로 이 기능을 제공한다.** 스토리지 볼륨은 파드와 같은 최상위 리소스는 아니지만, 파드의 일부분으로 정의되며 파드와 동일한 라이프사이클을 가진다.

파드가 여러개의 컨테이너를 가진 경우 모든 컨테이너가 볼륨을 공유할 수 있다.

## 볼륨 소개

쿠버네티스 볼륨은 파드의 구성 요소로 컨테이너와 동일하게 파드 스펙에서 정의된다. 볼륨은 파드의 모든 컨테이너에서 사용 가능하지만, 접근하려는 컨테이너에서 각각 마운트돼야 한다. 각 컨테이너에서 파일시스템의 어느 경로에나 볼륨을 마운트할 수 있다.

### 볼륨 예제

![](https://velog.velcdn.com/images/cksgodl/post/e0714736-cfe9-441d-b4e2-7df336f8bc2a/image.png)

리눅스에서는 파일시스템의 파일 트리의 임의 경로에 마운트할 수 있다. 즉 같은 볼륨을 두 개의 컨테이너에 마운트하면 컨테이너는 동일한 파일로 동작할 수 있다. 

### 사용가능한 볼륨 유형 소개

- emptyDir : 일시적인 데이터를 저장하는 데 사용되는 간단한 빈 디렉토리
- hostPath : 워커노드에 파일시스템을 파드의 디렉토리로 마운트하는데 사용
- gitRepo : 깃 레포지토리의 콘텐츠를 체크아웃해 초기화한 볼륨
- nfs : NFS 공유를 파드에 마운트한다.
- configMap, seceret, downwardAPI : 쿠버네티스 리소스나 클러스터 정보를 파드에 노출
- persistentVolumeClaim : 사전에 혹은 동적으로 프로비저닝된 퍼시스턴트 스토리지 사용


## 볼륨을 사용한 컨테이너 간 데이터 공유

하나의 파드에 있는 여러 컨테이너에서 데이터를 공유하는 방법을 알아보자.

### emptyDir 볼륨 사용

`emptyDir`볼륨은 동일 파드에서 실행 중인 컨테이너 간 파일을 공유할 때 유용하다. 

아래와 같이 디플로이먼트를 선언할 때 어떤 볼륨에 마운트할 것인지 적어준다.

```yaml
# values.yaml
sharedVolume:
  name: shared-volume
  sizeLimit: "1Gi"

container1:
  image: nginx
  volumeMounts:
    - name: shared-volume
      mountPath: /var/www/html

container2:
  image: busybox
  volumeMounts:
    - name: shared-volume
      mountPath: /data

# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      volumes:
        - name: {{ .Values.sharedVolume.name }} # emptyDir를 컨테이너 두개 위의 마운트한다.
          emptyDir: {}
      containers:
        - name: container1
          image: {{ .Values.container1.image }}
          volumeMounts:
            - name: {{ .Values.sharedVolume.name }}
              mountPath: {{ .Values.container1.volumeMounts.[0].mountPath }}
        - name: container2
          image: {{ .Values.container2.image }}
          volumeMounts:
            - name: {{ .Values.sharedVolume.name }}
              mountPath: {{ .Values.container2.volumeMounts.[0].mountPath }}
```

위와 같이 볼륨을 선언하면 콘테이너간 데이터를 공유할 수 있다. 하지만 포드가 종료되면 해당 볼륨마운트는 사라짐을 유의하라.


### 깃 레포지토리 볼륨

gitRepo볼륨은 기본적으로 `emptyDir`의 볼륨이며 파드가 시작되면 깃 레포지토리를 복제하고 체크아웃해 데이터로 채운다. 

> 간단하게 말하자면 시작 시점에 깃 레포지토리의 컨텐츠로 채워진 `emptyDir` 볼륨이다.


```yaml
# values.yaml
gitVolume:
  repository: "https://github.com/example/repository.git"
  revision: "main"
  mountPath: "/gitrepo"

mainContainer:
  image: "nginx"
  volumeMounts:
    - name: git-volume
      mountPath: "/app"

# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: main-container
          image: {{ .Values.mainContainer.image }}
          volumeMounts:
            - name: git-volume
              mountPath: "{{ .Values.gitVolume.mountPath }}"
      volumes:
        - name: git-volume
          gitRepo:
            repository: "{{ .Values.gitVolume.repository }}"
            revision: "{{ .Values.gitVolume.revision }}" # 브랜치를 의미한다.
            directory: . # 루트 디렉토리에 복제
```

> 엔터프라이즈 깃허브를 활용하는 경우 gitRepo에 대한 설정이 지원하지 않을수도 있는데 이런 경우에는 `initContainer`를 활용하여 emptyDir에 수동으로 깃 클론을 받는 방법을 활용하기도 한다.

이에 대한 동기화는 이뤄지지 않으며 파드가 삭제되고 재생성될 때 동기화가 된다. 그렇다고 꼭 포드를 재시작해야만 공유 콘테이너를 동기화할 수 있는 것은 아니다.

#### 사이드카 컨테이너

사이드카 컨테이너는 파드의 주 컨테이너의 동작을 보완하는 컨테이너이다. 해당 컨테이너를 활용하여 `git sync`명령어를 수행하여 파일 동기화를 유지하는 것을 권장한다.

## 워커 노드 파일시스템 파일 접근

대부분의 파드는 호스트 노드에 대한 정보가 없다. 따라서 노드의 파일시스템에 대해 접근할 수 없다.(접근하여서도 안된다.) 

그러나 노드의 파일을 읽거나 노드 디바이스에 접근하기 위해 노드의 파일시스템을 사용할 수 있는 방법을 `hostPath`를 통해 가능하게 한다.

### hostPath

`hostPath`볼륨은 노드 파일시스템의 특정 파일이나 디렉토리를 가르킨다. (파드 끼리의 공유 볼륨이라고 보아도 좋다.)

![](https://velog.velcdn.com/images/cksgodl/post/db1f505d-867f-4743-b1ae-d474b7188c1b/image.png)

이는 파드가 종료되도 삭제되지 않으며, 이전 파드와 동일한 노드에 스케줄링된다는 조건하에 이전 파드가 남긴 모든 항목을 볼 수 있다. (일반적으로 파드가 어떤 노드에 스케줄링되느냐에 따라 민감하기에 일반적인 파드에 사용하는 것은 좋은 생각이 아니다.)

```yaml
# values.yaml
hostPathVolume:
  path: "/data"
  name: "my-hostpath-volume"

mainContainer:
  image: "nginx"
  volumeMounts:
    - name: hostpath-volume
      mountPath: "/app"

# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: main-container
          image: {{ .Values.mainContainer.image }}
          volumeMounts:
            - name: hostpath-volume
              mountPath: "{{ .Values.hostPathVolume.path }}"
      volumes:
        - name: hostpath-volume
          hostPath:
            path: {{ .Values.hostPathVolume.path }}
            type: DirectoryOrCreate
```

선언 방법은 기존의 볼륨 선언방법과 비슷하다.

## 퍼시스턴스 스토리지의 활용

파드에서 실행 중인 어플리케이션이 디스크에 데이터를 유지해야 하고, 파드가 다른 노드로 재스케줄링된 경우에도 동일한 데이터를 활용해야 한다면 직므까지 언급한 볼륨 유형은 사용할 수 없다.


어떤 클러스터 노드에서도 접근이 필요한 데이터는 `NAS(Network Attached Storaged)`유형에 저장되어야 한다.

이는 쿠버네티스 클러스터가 어떤 클라우드 에서 실행되는지에 따라 예제가 모두 다르다.

_저자는 책에서 GCE(Google), AWS 등을 활용하는 예를 알려주지만 블로그 글에는 적지 않는다._

또한 `기반 스토리지 기술과 파드 분리`라는 주제로 퍼시스턴트볼륨클레임을 활용하여 외부 퍼시스턴트 볼륨과 연결하는 메니페스트 예제를 작성할 수 있다.


## 요약

- 다중 컨테이너 파드 생성에서 파드의 컨테이너들이 공유 마운트를 활용할 수 있다.
- `emptyDir`볼륨을 활용해 임시, 비영구 데이터를 저장한다.
- `gitRepo`볼륨을 사용해 시작 시점에 깃 레포 콘텐츠로 디렉토리를 채울 수 있다.
- `hostPath`볼륨을 사용해 호스트 노드의 파일에 접근한다.
- 외부스토리지 볼륨에 마운트해 파드가 재시작돼도 파드의 데이터를 유지할 수 있다.
- 퍼시스턴트 볼륨과 퍼시스턴트 볼륨 클레임을 활용해 파드와 스토리지 인프라 구조를 분리할 수 있다.






