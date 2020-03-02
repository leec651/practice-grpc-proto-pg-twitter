### user
a grpc service to manage user creation & relationship
- SignUp
- GetUser
- Login
- Follow
- Unfollow


### tweet
a grpc service for tweet crud operations
- Tweet
- Spam
- DeleteTweet
- GetTweet
- GetTweets

### proto
proto definition for user & tweet grpc service

### orm
db models with sql alchemy
- Favorite
- Follow
- Tweet
- User

### middleware
- auth.Authenticator decorator
- middleware.HandleGenericError decorator

### config
config ie. pg connection