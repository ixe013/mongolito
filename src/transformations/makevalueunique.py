from transformations import BaseTransformation

class MakeValuesUnique(BaseTransformation):
    def __init__(self, attribute):
        self.attribute = attribute

    def transform(self, ldapobject):
        '''Alex Martelli, order preserving. 
        Found at http://www.peterbe.com/plog/uniqifiers-benchmark

        '''
        seen = {}
        result = []

        try:
            for item in ldapobject[self.attribute]:
                marker = item
                # in old Python versions:
                # if seen.has_key(marker)
                # but in new ones:
                if marker in seen: continue
                seen[marker] = 1
                result.append(item)

            #Maybe we merged everything to a single item
            if len(result) == 1:
                #If so, make it single valued
                ldapobject[self.attribute] = result[0]
            else:
                #save the new list
                ldapobject[self.attribute] = result

        except KeyError:
            pass

        return ldapobject

