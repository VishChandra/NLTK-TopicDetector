#author='vishal'
import nltk, re
import os.path
import requests
from nltk import *
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

class TopicDetector(object):
    def tokenize_sent(self, words):
        data = sent_tokenize(words)
        content = [word_tokenize(sent) for sent in data]
        return content

    def grammar(self):
        grammar = r"""
                        NOUNS:
                            {<NN.*|JJ>*<NN.*>}
                            {<NN>+<NN>}
                            {<NNI>+<NN>}
                            {<JJ>+<NN>}
                            {<NNP>+<NNP>}
                            {<DT|NN>+}
                            {<DT><JJ><NN>}
                            {<NN>}
                            {<NNS>}
                            {<NNP>}
                            {<NNPS>}
                        """
        content = RegexpParser(grammar)
        return content

    def get_data(self, words):
        sents = word_tokenize(words)
        content1 = pos_tag(sents)
        content = self.grammar().parse(content1)
        return content

    def leaves(self, tree):
        tree = self.get_data(tree)
        for subtree in tree.subtrees(filter=lambda ts: ts.label() == 'NOUNS'):
            yield subtree.leaves()

    def get_set(self, tree):
        for l in self.leaves(tree):
            term = [w for w, t in l]
            yield term

    def improve_data(self, words):
        terms = self.get_set(words)
        keywords = []
        for term in terms:
            for word in term:
                keywords.append(word)
        keywords = ' '.join(keywords)
        sents = self.tokenize_sent(keywords)
        sents = [pos_tag(sent) for sent in sents]
        data = []
        for tagged in sents:
            for chunk in ne_chunk(tagged):
                if type(chunk) == Tree:
                    data.append(' '.join([c[0] for c in chunk]).lower())
        return data

    def most_common(self, words):
        data = word_tokenize(words)
        content = [word.lower() for word in data if word not in stopwords.words('english')]
        freq = FreqDist(content)
        return freq

    def extract_topics(self, words):
        freq = self.most_common(words)
        data = self.improve_data(words)
        top10 = [w for w, c in FreqDist(data).most_common(10)]
        topics = [e for e in top10 if e.split()[0] in freq]
        topics = self.readable(topics)
        topics = topics.title()
        return topics

    def main_topics(self, words):
        data = self.most_common(words)
        freq = [w for w, c in data.most_common(10)
                if pos_tag([w])[0][1] in "NNP"]
        et = word_tokenize(self.extract_topics(words).lower())
        main_topics = set([e for e in et if e.split()[0] in freq])
        main_topics = self.readable(main_topics)
        main_topics = main_topics.upper()
        return main_topics

    def most_freq(self, words):
        content = pos_tag(words)
        nouns = [w[0] for w in content if w[1] == "NN" or w[1] == "NNS"]
        freq = FreqDist(nouns)
        content = [w[0] for w in freq.most_common(7) if len(w[0]) > 3]
        content = self.readable(content)
        return content

    def readable(self, words):
        data = ', '.join(words)
        return data

    def download_file(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        document = ' '.join([p.get_text() for p in soup.find_all('p')])
        return document

    def get_input(self, result):
        ip = result
        words = []
        if ip == '1':
            print ("\nEnter/Paste and Press Ctrl+D to save it:\n")
            text = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                text.append(line)
            words = ' '.join(text)
        elif ip == '2':
            url = input("\nEnter URL: ")
            if re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?', url):
                words = self.download_file("{}".format(url))
            else:
                print("\nPlease enter correct URL")
                words = self.get_input(ip)
        elif ip == '3':
            file1 = "article.txt"
            file = input("(Press enter to use (DEFAULT: article.txt))\n\nEnter File Name: ")
            if os.path.isfile(file):
                data = open("{}".format(file), mode='r', errors='ignore')
                words = data.read()
            elif file == "":
                data = open("{}".format(file1), mode='r', errors='ignore')
                words = data.read()
            else:
                print("\nFile does not exist")
                words = self.get_input(ip)
        return words

def main():
    td = TopicDetector()
    print("============================")
    print("TOPIC DETECTOR")
    print("============================\n")
    print("1)Enter/Paste text \n2)Enter URL \n3)Enter File Location")
    ip = input("\nSelect Option: ")
    words = td.get_input(ip)
    print("\n----------------------------")
    print('The article contains {0} words'.format(len(word_tokenize(words))))
    print("--------------------")
    print('The most frequently occurred  words are {0}'.format(td.most_freq(word_tokenize(words))))
    print("---------------------------------------")
    print('The article is talking about {0}'.format(td.extract_topics(words)))
    print("----------------------------")
    print('The main topic of article is {0}'.format(td.main_topics(words)))
    print("----------------------------")

if __name__ == '__main__':
        main()