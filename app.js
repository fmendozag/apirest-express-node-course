const express = require('express')
const config = require('config')
const debug = require('debug')('app:inicio')
//const dbdebug = require('debug')('app:db')
//const logg = require('./logger')
const morgan = require('morgan')
const app = express()
const Joi = require('@hapi/joi')

app.use(express.json()) // body
app.use(express.urlencoded({extended:true}))
app.use(express.static('public'))

// Configuracion de entorno
console.log('Aplicacion: '+ config.get('nombre') )
console.log('BD server: '+ config.get('configDB.host'))
// Uso de middleware de tercero - Morgan

if(app.get('env') === 'development') {
    app.use(morgan('tiny'))
    //console.log('Morgan Habilitado')
    debug('Morgan esta habilitado')
}

// Trabajos con la base de datos
debug('Conectando con la base de datos')

/*app.use(logg)
app.use(function (req,res,next) {
    console.log('autenticando....')
    next()
})*/

const users = [
    {id:1, name:'Freddy'},
    {id:2, name: 'Maritza'},
    {id:3, name: 'Liam'},
    {id:4, name: 'Jared'}
]


app.get('/api/users', (req,res) => {
    res.send(users)
})



app.get('/api/users/:id',(req,res) => {
    let user = existsUser(req.params.id)
    if(!user)
        res.status(404).send('el usuario no fue encontrado')
    else
        res.send(user)

})

app.post('/api/users',(req,res) => {
    const {error, value} = validarUser(req.body.name)
    if(!error){
        const user = {
            id:users.length+1,
            name:value.name
        }
        users.push(user)
        res.send(user)}
    else {
        const mensaje = error.details[0].message
        res.status(400).send(mensaje)
    }
}) //
app.put('/api/users/:id',(req,res) => {
    let user = existsUser(req.params.id)
    if(!user) {
        res.status(404).send('ele usuario no fue encontrado')
        return
    }

    const {error, value} = validarUser(req.body.name)
    if (error){
        const msj = error.details[0].message
        res.status(400).send(msj)
        return
    }

    user.name = value.name
    res.send(user)
})

app.delete('/api/users/:id',(req,res) =>{
    let user = existsUser(req.params.id)
    if(!user){
        res.status(400).send('No se encontro al usuario')
        return
    }
    const i = users.indexOf(user)
    users.splice(i,1)

    res.send(users)
})

const port = process.env.PORT || 3000
app.listen(port, () =>{
    console.log(`Escuchando en el puerto ${port}...`)
})



function existsUser(id) {
    return users.find( u => u.id === parseInt(id)  )
}

function validarUser(nm) {
    const schema = Joi.object({
        name: Joi.string().min(3).required()
    })
    return (schema.validate({name: nm}))
}




