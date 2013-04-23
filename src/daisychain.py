'''A simple wrapper that allows to daisy chain operations.

Adapted from Gist found at https://gist.github.com/bukzor/2466345
'''

class Pipeline(object):
    def __init__(self, *functions, **kwargs):
        self.functions = functions
        self.data = kwargs.get('data')
 

    def __call__(self, data):
        return TransformationPipeline(*self.functions, data=data)
 
 
    def __iter__(self):
        data = self.data
        for func in self.functions:
            data = func(data)
        return data
 
