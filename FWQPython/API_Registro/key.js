const nodeRSA = require('node-rsa')

const key = new nodeRSA({b:1024})
let secret = "Mensaje secreto"

/*var encryptedString = key.encrypt(secret, 'base64')
console.log(encryptedString);

var decryptedString = key.decrypt(encryptedString, 'utf-8')
console.log(decryptedString);*/

//var public_key = key.exportKey('public')
//var private_key = key.exportKey('private')

public_key = '-----BEGIN PUBLIC KEY-----\n' +
'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCP/d3Hn0dxXMG88tVKeuuOottz \n' +
'88kualPEZInju9HaRnUtuXf8VqdUkZG2FmurtEEdFFBnF9kGH8EnE7ZnjTxr5exh \n' +
'Q9Ocee4rWdad7bFeNPokrB9fKIp+BL2jI16GPuGyG90ZY1LEH5cGBfVFQQhSZOw5 \n' +
'a+oXvZibqtrhkA7iOQIDAQAB \n' +
'-----END PUBLIC KEY-----'

private_key = '-----BEGIN RSA PRIVATE KEY-----\n' + 
'MIICXAIBAAKBgQCP/d3Hn0dxXMG88tVKeuuOottz88kualPEZInju9HaRnUtuXf8 \n' +
'VqdUkZG2FmurtEEdFFBnF9kGH8EnE7ZnjTxr5exhQ9Ocee4rWdad7bFeNPokrB9f \n' +
'KIp+BL2jI16GPuGyG90ZY1LEH5cGBfVFQQhSZOw5a+oXvZibqtrhkA7iOQIDAQAB \n' +
'AoGAOhAZrVRqH6lSqlmVboowkHzVV2V3u5K+opQUElP7ZDRDLiP64TMkGHL2ueFC \n' +
'm6N9GjfF0DyKk/CcF6DYTdtjAFTRhuz3RThQ05aYMIRXIaq4hpBJjnYlsc+rVpKK \n' +
'Tf+ZTE6Y4J1F9umAcOrwY6s6Sijn6ue7yELIw0lOwlMptE0CQQDu575gXzUvTjM1 \n' +
'j6/rG/4oSuKxSllIDuVZzMdEB9t1pIQMycVCMPar09D5A9i9WljW5+oSAutT8SpH \n' +
'naQFmppTAkEAmkt/51tP6654xapqLvQiS8PPmMdMf5nZdgJhY++tws3Mik2GxZzd \n' +
'fU0FYHi8j/GdptWXUdspXZB74Mh54d63wwJBAJfnxLY0c3XTzF3nMh1VXEK0cvX1 \n' +
'51UZG54Axkcsk892vvv+o62VwpK5CSv81Sh5NPnY1o2DS6zBMHf+9VcW2b8CQEoP \n' +
'TUBemvj0UPIH/1m0QzX8sguSNgzVawTy1Y5jgBMON0x3M+Zsif/X1Wnd6hxpjBOF \n' +
'WFGpEazgaiWV9LLO9YMCQD1K6kY5RIUOeFZ1wItoiL/QghaCw9Jhy3eQQ52t8Zu8 \n' +
'ezgYoUQjy7JsN0vOQlx6xD2XhQsdNGz6P3+lOwCNSAI= \n' +
'-----END RSA PRIVATE KEY-----'

let key_private = new nodeRSA(private_key)
let key_public = new nodeRSA(public_key)

var encryptedString = key_public.encrypt(secret, 'base64')
console.log(encryptedString);

var decryptedString = key_private.decrypt(encryptedString, 'utf-8')
console.log(decryptedString);



