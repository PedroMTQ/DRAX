
from source.Fetchers.Reaction_Fetchers.Reaction_Fetcher import *


class Reaction_Fetcher_KEGG(Reaction_Fetcher):
    def __init__(self,reaction_id,extra_args={},memory_storage=None,init_Fetcher=True):
        Reaction_Fetcher.__init__(self,reaction_id=reaction_id,memory_storage=memory_storage)
        self.db = 'kegg'
        self.set_convergence_args(extra_args)
        if init_Fetcher:
            self.reaction= self.get_reactions_KEGG()
            self.add_reaction()

    def set_convergence_args(self,extra_args):
        if 'compound' in extra_args: self.convergence_args['compound'] = extra_args['compound']
        else: self.convergence_args['compound']=None
        #For convergence
        self.convergence_args['proteins_list']=[]


    def rn_enzyme(self, rn_soup):
        enzyme_ec = rn_soup.find('nobr', text=re.compile('Enzyme'))
        if enzyme_ec:
            enzyme_ec = enzyme_ec.findNext('td').text.strip('\n')
        return enzyme_ec

    def fix_rn_comp_id(self,rn_comp_id):
        res=[]
        for stoi,cpd in rn_comp_id:
            cpd_str=re.search('[A-Z]+\d+',cpd)
            if cpd_str:
                cpd=cpd_str.group()
            res.append([stoi,cpd])
        return res

    def reaction_info_KEGG(self, rn_id):
        url = 'http://www.kegg.jp/dbget-bin/www_bget?rn:' + rn_id
        webpage = self.get_with_fetcher(url)
        if not webpage: return None
        soup = BeautifulSoup(webpage, 'lxml')
        rn_info = {'rn': self.textbox_KEGG(soup, 'Definition'), 'rn_comp_id': self.textbox_KEGG(soup, 'Equation')}
        rn_info['rn_comp_id'],complete_l,len_sub = get_stoichiometry(rn_info['rn'], rn_info['rn_comp_id'])
        rn_info['rn_comp_id']=self.fix_rn_comp_id(rn_info['rn_comp_id'])
        #For example R00382 will have DNA(n+m), this way we just keep the ID and not the multipliers
        for i in rn_info['rn_comp_id']:
            i[1]=i[1].split('(')[0]
        rn_info['pathways'] = self.textbox_KEGG(soup, 'Pathway',to_split=True)
        rn_with_instances = self.reaction_met_instances(rn_info['rn'], rn_info['rn_comp_id'], 'kegg')
        #now we convert kegg ids to instances (after rn_with_instances since we were fetching info for cpds)
        rn_info['rn_instances'] = rn_with_instances
        return rn_info, soup

    def find_id_api_search(self,compound):
        search = self.get_with_fetcher(compound,api_kegg=True, database='cpd')
        for i in search:
            ids, names = i.split('\t')
            for j in names.split(';'):
                j = j.strip()
                if j.lower() == compound.lower(): return ids[4:]
        return False

    def check_correct_api_kegg_search(self,rn_with_ids, compound=None):
        if not compound: return True
        kegg_id = self.find_id_api_search(compound)
        for i in rn_with_ids:
            if i[1] == kegg_id: return True
        return False

    # End goal function for kegg
    def get_reactions_KEGG(self):

        rn_info_rn_soup = self.reaction_info_KEGG(self.reaction_id)
        if rn_info_rn_soup:
            rn_info, rn_soup= rn_info_rn_soup
            if self.check_correct_api_kegg_search(rn_info['rn_comp_id'], self.convergence_args['compound']):
                enzyme_ec = self.rn_enzyme(rn_soup)
                if enzyme_ec:
                    self.convergence_args['proteins_list'] = [i for i in enzyme_ec.split() if not i.endswith('-')]
                orthology = self.textbox_KEGG(rn_soup, 'Orthology', to_split=True)
                if orthology: orthology = [i.split(' : ')[0] for i in orthology]
                res = {
                    'kegg': self.reaction_id,
                    'reaction_str': rn_info['rn'],
                    'pathways':  rn_info['pathways'],
                    'kegg_ko':  orthology,
                }
                if rn_info['rn_instances']: res['reaction_with_instances'] = rn_info['rn_instances']
                else:                       res['rn_with_ids'] = [rn_info['rn'], rn_info['rn_comp_id'], 'kegg']
                return Reaction(res)
            else:
                print('KEGG API returned a reaction from another compound! Reaction not added')

    def converge_reaction_global(self):
        self.converge_reaction_to_protein()

    def converge_reaction_rpg(self):
        #RP part of the CRPG pipeline
        self.converge_reaction_to_protein()

    def converge_reaction_to_protein(self):
        for enzyme_ec in self.convergence_args['proteins_list']:  # there may be several enzymes for the same reaction
            protein_instance = self.find_protein(query_id=enzyme_ec)
            if protein_instance:
                self.get_reaction().set_detail('protein_instances',protein_instance,converged_in=self.db)

if __name__ == '__main__':
    rn_search=Reaction_Fetcher_KEGG('R02887')
    r=rn_search.get_reaction()
    print(r)
