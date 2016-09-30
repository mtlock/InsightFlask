def ModelIt(fromUser  = 'Default', tweets = []):
  in_hashtag = len(tweets)
  print 'The number of tweets with this hashtag is %i' % in_hashtag
  result = in_hashtag
  if fromUser != 'Default':
    return result
  else:
    return 'check your input'
