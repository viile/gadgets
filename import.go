package main

import (
	"fmt"
	"flag"
	"io"
	"io/ioutil"
	"os"
	"encoding/csv"
	"encoding/json"
	"strings"
	"bytes"
	"crypto/sha1"
	"net/http"
	//"bufio"
)

var infile *string = flag.String("i","infile","please choose import file")
var url *string = flag.String("u","url","please input url address")
var appid *string = flag.String("a","appid","please input appid")
var secretKey *string = flag.String("s","secretKey","please input secret key")

type Register struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Nickname string `json:"nickname"`
	Avatar string `json:"avatar"`
	Phone string `json:"phone"`
	Gender int `json:"gender"`
	Role_id int `json:"role_id"`
	Class_name string `json:"class_name"`
	School_name string `json:"school_name"`
}

func main(){
	flag.Parse()
	fmt.Println(*infile,*url,*appid,*secretKey)

	file,err := os.Open(*infile)
	if err != nil {
		fmt.Println("Error: ",err)
		return
	}
	defer file.Close()

	reader := csv.NewReader(file)
	k := 0
	for {
		record,err := reader.Read()
		if err == io.EOF {
			break
		} else if err != nil {
			fmt.Println("Error: ",err)
			return
		}
		if k > 0 {
			fmt.Println(record)
			data := Register{
				Username :record[0],
				Password :record[1],
				School_name :record[2],
				Class_name : record[3],
				Role_id : getRole(record[4]),
				Nickname : record[5],
				Gender : getGender(record[6]),
				Phone : record[7],
				Avatar : "",
			}
			jsondata, err := json.Marshal(data)
			if err != nil {
				fmt.Println("Error:", err)
			}
			result := request(*url,*appid,*secretKey,jsondata)
			fmt.Println(result)
		}
		k = k + 1
	}
}
func getGender(gender string) int {
	if gender == "男" {
		return 1
	}
	return 2
}
func getRole(role string) int {
	if role == "学生" {
		return 1
	}
	return 2
}
func encry(data string) string {
	t := sha1.New();
	io.WriteString(t,data);
	return strings.ToUpper(fmt.Sprintf("%x",t.Sum(nil)));

}
func request(url ,appid, secretKey string,data []byte) string {
	client := &http.Client{}
	req, err := http.NewRequest("POST",url,bytes.NewReader(data))
	req.Header.Add("appid",appid)
	req.Header.Add("sign",encry(string(data)))
	res,err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		panic("http error")
	}
	defer res.Body.Close()
	body,err := ioutil.ReadAll(res.Body)
	return string(body)
}
