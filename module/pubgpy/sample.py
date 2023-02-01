"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .models import PUBGModel
from .enums import Platforms, get_enum


class Sample(PUBGModel):
    """ Sample objects contain the ID of a match.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    client :
        Contains PUBGpy's main client class.
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the sample response
    type : str
        Identifier for this object type
    shard : Platforms
        Type of shard ID
    created_at : str
        Time when Sample Data was created.
    title : str
        Type of title
    matches : list
        Sample Imported Match Data
    """
    def __init__(self, client, data):
        self.data = data
        self.client = client

        self.type = self.data.get("type")
        self.id: int = self.data.get("id")
        super().__init__(self)

        attributes = self.data.get("attributes")
        self.created_at: str = attributes.get("createdAt")
        self.title: str = attributes.get("titleId")
        self.shard: Platforms = get_enum(Platforms, attributes.get("shardId"))

        relationships = self.data.get("relationships")
        self.matches = [i.get("id") for i in relationships.get("matches", {}).get("data", [])]

    async def match(self, position: int = 0):
        """
        Recall match dates in sample data to suit the location.

        Parameters
        ----------
        position : int
            location of matches list

        Returns
        -------
        Matches :
            Contains classes for Matches.
        """
        if position > len(self.matches):
            raise IndexError("list index out of Match List")
        return await self.client.matches(match_id=self.matches[position])
