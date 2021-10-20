const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const saltRounds = 10;

const UserSchema = new mongoose.Schema({
    username: {type: String, required: true, unique: true},
    nombre: {type: String, required: true},
    password: {type: String, required: true}
});

UserSchema.pre('save', function(next) {
    if(this.isNew || this.isModified('password')){
        const document = this;

        bcrypt.hash(document.password, saltRounds, (err, hashedPassword) =>{
            if(err){
                next(err);
            }else{
                document.password = hashedPassword;
                next();
            }
        })
    }else{
        next();
    }

})

module.exports = mongoose.model('User', UserSchema);
