package main

import (
	"fmt"
	"time"
	"sync"
)

type Test struct {
	name string "test"
}

func gen(done <-chan struct{},nums ...int) <-chan int {
	out := make(chan int,len(nums))
	for _,n := range nums {
		out <- n
	}
	close(out)
	return out
}

func sq(done <-chan struct{}, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			select {
				case out <- n * n :
				case <-done:
					return
			}
		}
	}()
	return out
}

func merge(done <-chan struct{},cs ...<-chan int) <-chan int {
	var wg sync.WaitGroup
	out := make(chan int,1)
	output := func(c <-chan int) {
		for n := range c {
			select {
			case out <- n:
			case <-done:
			}
		}
		wg.Done()
	}
	wg.Add(len(cs))
	for _, c := range cs {
		go output(c)
	}

	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}

func test(){
	var wg sync.WaitGroup
	ch := make(chan int,20)
	wg.Add(20)
	for i:=0;i<20;i++{
		fmt.Println(time.Now())
		ch <- i
		go func(){
			fmt.Println(time.Now(),<-ch)
			wg.Done()
		}()
	}

	wg.Wait()
}

func xrange() chan int {
	ch := make(chan int)
	go func () {
		for i:=2;;i++{
			ch <- i
		}
	}()

	return ch
}

func res(user string) chan string {
	notify := make(chan string)
	go func() {
		notify <- fmt.Sprintf("hi,%s",user)
	}()

	return notify
}

func stu(x int) int {
	return 100 -  x
}

func branch(x int) chan int {
	ch := make(chan int)
	go func(){
		ch <- stu(x)
	}()

	return ch
}

func fan(chs ... chan int) chan int {
	ch := make(chan int)
	for _,c := range chs {
		go func(c chan int){ch <- <- c}(c)
	}
	return ch
}

func foo(i int) chan int {
	ch := make(chan int)
	go func(){ch <- i}()
	return ch
}

func filter(in chan int,number int) chan int {
	out := make(chan int)
	go func(){
		for {
			i := <-in
			//fmt.Println("filter <-in ",i," number ",number)
			//time.Sleep(1 * time.Second)
			if i % number != 0 {
				out <- i
			}
		}
	}()
	return out
}

func main(){
	fmt.Println(time.Now())

	const max = 10000000
	nums := xrange()
	number := <-nums
	for number <= max {
		fmt.Println(number)
		nums = filter(nums,number)
		number = <-nums
	}
	/*
	c1,c2,c3 := foo(1),foo(2),foo(3)
	c := make(chan int)
	go func(){
		for {
			select {
				case v1 := <-c1 : c <- v1
				case v2 := <-c2 : c <- v2
				case v3 := <-c3 : c <- v3
			}
		}
	}()
	fmt.Println(<-c,<-c,<-c)
	*/
	//jack := res("jack")
	//fmt.Println(<-jack)

	//res := fan(fan(fan(branch(3))))
	//for i:=0;i<3;i++{
	//	fmt.Println(<-res)
	//}
	/*
	done := make(chan struct{})
	defer close(done)
	cc := gen(done,2,3)
	c1 := sq(done,cc)
	c2 := sq(done,cc)
	out := merge(done,c1,c2)
	for n := range out {
		fmt.Println("received:",n)
	}
	*/

	//generator := xrange()
	//for i:=0;;i++ {
	//	fmt.Println(<-generator)
	//}
	//test()
	//time.Sleep(10 * time.Second)
}
