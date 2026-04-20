import{d as y,j as _,a as e,t as c,u as s,b as o,w as m,q as g,r as i,e as f,o as b}from"./index-CiTZzLRI.js";import{c as n}from"./createLucideIcon-6adTPsOq.js";/**
 * @license lucide-vue-next v0.469.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const w=n("LayoutDashboardIcon",[["rect",{width:"7",height:"9",x:"3",y:"3",rx:"1",key:"10lvy0"}],["rect",{width:"7",height:"5",x:"14",y:"3",rx:"1",key:"16une8"}],["rect",{width:"7",height:"9",x:"14",y:"12",rx:"1",key:"1hutg5"}],["rect",{width:"7",height:"5",x:"3",y:"16",rx:"1",key:"ldoo1y"}]]);/**
 * @license lucide-vue-next v0.469.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const k=n("LogOutIcon",[["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}],["polyline",{points:"16 17 21 12 16 7",key:"1gabdz"}],["line",{x1:"21",x2:"9",y1:"12",y2:"12",key:"1uyos4"}]]);/**
 * @license lucide-vue-next v0.469.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const v=n("UserIcon",[["path",{d:"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2",key:"975kel"}],["circle",{cx:"12",cy:"7",r:"4",key:"17ys0d"}]]),L={class:"min-h-screen flex"},D={class:"w-64 bg-slate-900 text-white flex flex-col"},R={class:"p-6 border-b border-slate-700"},V={class:"text-sm text-slate-400 capitalize mt-1"},C={class:"flex-1 p-4 space-y-1"},I={class:"p-4 border-t border-slate-700"},S={class:"flex items-center gap-3 px-4 py-2"},z={class:"text-sm truncate"},B={class:"flex-1 overflow-auto"},U={class:"p-8"},O={__name:"DashboardLayout",setup(H){const a=y(),d=f();async function u(){await a.logout(),d.push("/login")}return(h,t)=>{var r,l;const p=i("RouterLink"),x=i("RouterView");return b(),_("div",L,[e("aside",D,[e("div",R,[t[0]||(t[0]=e("h1",{class:"text-xl font-bold"},"Supervisor System",-1)),e("p",V,c(s(a).role),1)]),e("nav",C,[o(p,{to:`/${s(a).role}`,class:g(["flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-700 transition",{"bg-slate-700":(r=h.$route.name)==null?void 0:r.includes("Dashboard")}])},{default:m(()=>[o(s(w),{class:"w-5 h-5"}),t[1]||(t[1]=e("span",null,"Dashboard",-1))]),_:1},8,["to","class"])]),e("div",I,[e("div",S,[o(s(v),{class:"w-5 h-5"}),e("span",z,c(((l=s(a).user)==null?void 0:l.fname)||"User"),1)]),e("button",{onClick:u,class:"w-full mt-2 flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-600 transition text-sm"},[o(s(k),{class:"w-5 h-5"}),t[2]||(t[2]=e("span",null,"Logout",-1))])])]),e("main",B,[e("div",U,[o(x)])])])}}};export{O as default};
