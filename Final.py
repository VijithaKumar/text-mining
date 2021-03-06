import pandas
import numpy
import nltk
import re
import sklearn
from sklearn.pipeline import Pipeline,TransformerMixin,FeatureUnion
from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import cross_val_predict
from sklearn import svm
from sklearn import metrics
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn import preprocessing
from sklearn import decomposition
from nltk.corpus import stopwords, treebank
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

df = pandas.read_csv("/Users/Vijitha/Desktop/Spring/IDS 566/wikipedia.annotated_train-2.csv")

pos=pandas.read_csv("/Users/Vijitha/Desktop/Spring/IDS 566/Positive words.csv")
positive=pos["Words"]
neg=pandas.read_csv("/Users/Vijitha/Desktop/Spring/IDS 566/Negative words.csv")
negative=neg["Words"]

Y=df['politeness'].as_matrix()

X=df['Request']

# Word lists

hedges = [
    "think", "thought", "thinking", "almost",
    "apparent", "apparently", "appear", "appeared", "appears", "approximately", "around",
    "assume", "assumed", "certain amount", "certain extent", "certain level", "claim",
    "claimed", "doubt", "doubtful", "essentially", "estimate",
    "estimated", "feel", "felt", "frequently", "from our perspective", "generally", "guess",
    "in general", "in most cases", "in most instances", "in our view", "indicate", "indicated",
    "largely", "likely", "mainly", "may", "maybe", "might", "mostly", "often", "on the whole",
    "ought", "perhaps", "plausible", "plausibly", "possible", "possibly", "postulate",
    "postulated", "presumable", "probable", "probably", "relatively", "roughly", "seems",
    "should", "sometimes", "somewhat", "suggest", "suggested", "suppose", "suspect", "tend to",
    "tends to", "typical", "typically", "uncertain", "uncertainly", "unclear", "unclearly",
    "unlikely", "usually", "broadly", "tended to", "presumably", "suggests",
    "from this perspective", "from my perspective", "in my view", "in this view", "in our opinion",
    "in my opinion", "to my knowledge", "fairly", "quite", "rather", "argue", "argues", "argued",
    "claims", "feels", "indicates", "supposed", "supposes", "suspects", "postulates"
]

acro = pandas.read_csv(r"/Users/Vijitha/Desktop/Spring/IDS 566/Text acronym.csv")
text=numpy.asarray(acro["T"])
actual=numpy.asarray(acro["A"])

def cleaner(s):
    ss=re.sub(r'[^a-zA-Z]', ' ', s) #keeps alpha

    tokens = nltk.word_tokenize(ss)
    tokens_lower=map(lambda x:x.lower(),tokens) #convert all words to lower
    replaced = []
    for item in tokens_lower:
        words = item
        for i, j in enumerate(text):
            if item == j:
                words = item.replace(item, actual[i])
        replaced.append(words)
    filtered_words = [word for word in replaced if word not in stopwords.words('english')] #remove all stop words
    remove_url = [word for word in filtered_words if not "url" in word] #remove 'url'
    return remove_url

vectorizer = TfidfVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)

class Hedgeser(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: len(set(nltk.word_tokenize(l.lower())).intersection(hedges))))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Poser(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: len(set(nltk.word_tokenize(l.lower())).intersection(set(positive)))))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Neger(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: len(set(nltk.word_tokenize(l.lower())).intersection(set(negative)))))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class POSTaggerMD(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: sum(1 for x in dict(nltk.pos_tag(s)).values() if x=='MD')))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class POSTaggerPRP(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: sum(1 for x in dict(nltk.pos_tag(s)).values() if x=='PRP' or x=='PRP$')))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class POSTaggerWD(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: sum(1 for x in dict(nltk.pos_tag(s)).values() if x=='RB' or x=='RBR' or x=='RBS')))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class POSTaggerJJ(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: sum(1 for x in dict(nltk.pos_tag(s)).values() if x=='JJ' or x=='JJR' or x=='JJS')))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class POSTaggerVB(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: sum(1 for x in dict(nltk.pos_tag(s)).values() if x=='VBD' or x=='VBN')))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class SubjunctiveTransformer(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: "could you" in s.lower() or "would you" in s.lower()))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class IndicativeTransformer(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: "can you" in s.lower() or "will you" in s.lower()))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Gratitude(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: "i appreciate" in s.lower() or "thank" in s.lower()))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Deference(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: s.partition(' ')[0].lower() in ["great","good","nice","good","interesting","cool","excellent","awesome"]))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Greeting(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: s.partition(' ')[0].lower() in ["hi","hello","hey"]))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class DirectStart(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: s.partition(' ')[0].lower() in ["so","then","and","but","or"]))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class FirstpStart(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: s.partition(' ')[0].lower() in ["i","my","mine","myself"]))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class FirstpPlural(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: len(set(nltk.word_tokenize(l.lower())).intersection(["we", "our", "us", "ourselves"]))>0))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class SecondPerson(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: (len(set(nltk.word_tokenize(l.lower())).intersection(["you","your","yours","yourself"]))>0)and (l.partition(' ')[0].lower() not in ["you","your","yours","yourself"])))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class SecondpStart(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: s.partition(' ')[0].lower() in ["you","your","yours","yourself"]))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class PleaseStart(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: s.partition(' ')[0].lower() in ["please"]))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class FirstPerson(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: (len(set(nltk.word_tokenize(l.lower())).intersection(["i", "my", "mine", "myself"]))>0)and (l.partition(' ')[0].lower() not in ["i", "my", "mine", "myself"])))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Please(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: (len(set(nltk.word_tokenize(l.lower())).intersection(["please"]))>0)and (l.partition(' ')[0].lower() not in ["please"])))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Factuality(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda l: (len(set(nltk.word_tokenize(l.lower())).intersection(["really", "actually", "honestly", "surely"]))>0) or "the point" in l.lower() or "the reality" in l.lower() or "the truth" in l.lower() or "in fact" in l.lower()))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Question(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: s.partition(' ')[0].lower() in ["please"]))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Bytheway(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: "by the way" in s.lower()))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Apologizing(TransformerMixin):

    def transform(self, X, **transform_params):
        modals = DataFrame(X.apply(lambda s: len(set(nltk.word_tokenize(s.lower())).intersection(["sorry", "whoops","oops","excuse", "regret", "admit","plea",]))>0 or "i apologize" in s.lower() or "forgive me" in s.lower() or "excuse me" in s.lower()))
        return modals

    def fit(self, X, y=None, **fit_params):
        return self

class Norm(TransformerMixin):

    def transform(self, X, **transform_params):
        return DataFrame(preprocessing.normalize(X))

    def fit(self, X, y=None, **fit_params):
        return self

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print "Topic %d:" % (topic_idx)
        print " ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]])


# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, tokenizer=cleaner,stop_words='english')
tf = tf_vectorizer.fit_transform(X)
tf_feature_names = tf_vectorizer.get_feature_names()

no_topics = 3

# Run LDA
lda = LatentDirichletAllocation(n_topics=no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0)
lda.fit(tf)

print("\nTopics in LDA model:")
#display_topics(lda, tf_feature_names, 30)

class ModelTransformer(TransformerMixin):

    def __init__(self, model):
        self.model = model

    def fit(self, *args, **kwargs):
        self.model.fit(*args, **kwargs)
        return self

    def transform(self, X, **transform_params):
        return DataFrame(self.model.predict(X))


combined_features= FeatureUnion([("tfd",vectorizer),
                                ("pos",SubjunctiveTransformer()),
                                ("pos1",IndicativeTransformer()),
                                ("try", Pipeline([
                                    ('modal',POSTaggerMD()),
                                    ('scale', Norm())
                                    ])),
                                ("try1", Pipeline([
                                    ('pro',POSTaggerPRP()),
                                    ('scale', Norm())
                                    ])),
                                ("try2", Pipeline([
                                    ('wd',POSTaggerWD()),
                                    ('scale', Norm())
                                    ])),
                                ("try3", Pipeline([
                                    ('adj',POSTaggerJJ()),
                                    ('scale', Norm())
                                    ])),
                                ("try4", Pipeline([
                                    ('verb',POSTaggerVB()),
                                    ('scale', Norm())
                                    ])),
                                ("hedges", Pipeline([
                                    ('hed',Hedgeser()),
                                    ('scale',Norm())
                                    ])),
                                ("positive",Pipeline([
                                    ('posi',Poser()),
                                    ('scale',Norm())
                                    ])),
                                ("negative",Pipeline([
                                    ('nega',Neger()),
                                    ('scale',Norm())
                                    ])),
                                ("gratitude",Gratitude()),
                                ("deference",Deference()),
                                ("greeting", Greeting()),
                                ("dstart", DirectStart()),
                                ("firststart", FirstpStart()),
                                ("firstplu", FirstpPlural()),
                                ("secper", SecondPerson()),
                                ("secpstart", SecondpStart()),
                                ("pls", PleaseStart()),
                                ("fp", FirstPerson()),
                                ("please", Please()),
                                ("fact", Factuality()),
                                ("qs", Question()),
                                ("btw", Bytheway()),
                                ("sorry", Apologizing())
                                ])


X_features = combined_features.fit(X, Y).transform(X)
X_features.toarray()
#X_normalized = preprocessing.normalize(X_features)

#print X_features.toarray().shape
#print X_features[:,57486]
#print X_features[:,57488]

clf = svm.SVC(kernel='linear', C = 1.0)
clf.fit(X_features,Y)

dftest = pandas.read_csv("/Users/Vijitha/Desktop/Spring/IDS 566/wikipedia.annotated_test.csv")

Y1=dftest['Label'].as_matrix()

X1=dftest['Request']

Test_features=combined_features.transform(X1)
#Test_normalized=preprocessing.normalize(Test_features,norm="l1")

#pred = clf.predict(Test_features.toarray())
pred=cross_val_predict(clf, Test_features, Y1, cv=5)
#pred = cross_val_predict(clf,X_features,Y,cv=5)

print(metrics.classification_report(Y1, pred))
print(metrics.confusion_matrix(Y1,pred))

print "score"
print metrics.accuracy_score(Y1, pred)
'''
# prepare configuration for cross validation test harness
seed = 7
# prepare models
models = []
models.append(('LR', LogisticRegression(solver="lbfgs")))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))
models.append(('SVM', SVC()))
# evaluate each model in turn
results = []
names = []
scoring = 'accuracy'
for name, model in models:
	kfold = model_selection.KFold(n_splits=10, random_state=seed)
	cv_results = model_selection.cross_val_score(model, Test_features.toarray(), Y1, cv=kfold, scoring=scoring)
	results.append(cv_results)
	names.append(name)
	msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
	print(msg)

'''
